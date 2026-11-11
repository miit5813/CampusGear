"""Бизнес-логика бронирования: проверка доступности и смена статусов заявки."""
from datetime import date, datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Booking, BookingStatusHistory, Equipment, EquipmentUnit, User
from app.models.enums import AllowedFor, BookingStatus, UnitStatus, UserType

# Заявки в этих статусах занимают экземпляр оборудования на свои даты
OCCUPYING_STATUSES = (BookingStatus.APPROVED, BookingStatus.ISSUED, BookingStatus.OVERDUE)

# Эти заявки пользователь ещё может отменить
CANCELLABLE_STATUSES = (BookingStatus.PENDING, BookingStatus.APPROVED)


def validate_period(start_date: date, end_date: date) -> None:
    if end_date < start_date:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Дата окончания раньше даты начала")


def free_units(db: Session, equipment_id: int, start_date: date, end_date: date):
    """Возвращает (все пригодные экземпляры, свободные на период экземпляры).

    Периоды пересекаются, если одна аренда началась не позже конца другой
    и закончилась не раньше её начала.
    """
    units = db.scalars(
        select(EquipmentUnit)
        .where(
            EquipmentUnit.equipment_id == equipment_id,
            EquipmentUnit.status.not_in([UnitStatus.MAINTENANCE, UnitStatus.WRITTEN_OFF]),
        )
        .order_by(EquipmentUnit.id)
    ).all()

    busy_ids = set(
        db.scalars(
            select(Booking.unit_id).where(
                Booking.equipment_id == equipment_id,
                Booking.status.in_(OCCUPYING_STATUSES),
                Booking.unit_id.is_not(None),
                Booking.start_date <= end_date,
                Booking.end_date >= start_date,
            )
        )
    )
    return units, [unit for unit in units if unit.id not in busy_ids]


def add_history(
    booking: Booking,
    old_status: Optional[BookingStatus],
    new_status: BookingStatus,
    changed_by: int,
    comment: Optional[str] = None,
) -> None:
    """Дописывает запись в журнал смены статусов."""
    booking.status_history.append(
        BookingStatusHistory(
            old_status=old_status.value if old_status else None,
            new_status=new_status.value,
            changed_by=changed_by,
            comment=comment,
        )
    )


def create_booking(db: Session, user: User, data) -> Booking:
    equipment = db.scalar(
        select(Equipment)
        .where(Equipment.id == data.equipment_id, Equipment.is_active.is_(True))
        .options(selectinload(Equipment.terms))
    )
    if equipment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Оборудование не найдено")

    validate_period(data.start_date, data.end_date)
    if data.start_date < date.today():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Дата начала не может быть в прошлом")

    terms = equipment.terms
    if terms is not None:
        days = (data.end_date - data.start_date).days + 1
        if days > terms.max_days:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Максимальный срок аренды этого оборудования: {terms.max_days} дн.",
            )
        if terms.allowed_for == AllowedFor.EMPLOYEE and user.user_type != UserType.EMPLOYEE:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Это оборудование доступно только сотрудникам")
        if terms.allowed_for == AllowedFor.STUDENT and user.user_type != UserType.STUDENT:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Это оборудование доступно только студентам")

    # Не даём подать вторую заявку на то же оборудование на пересекающиеся даты
    duplicate = db.scalar(
        select(Booking.id).where(
            Booking.user_id == user.id,
            Booking.equipment_id == equipment.id,
            Booking.status.in_((BookingStatus.PENDING,) + OCCUPYING_STATUSES),
            Booking.start_date <= data.end_date,
            Booking.end_date >= data.start_date,
        )
    )
    if duplicate is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "У вас уже есть заявка на это оборудование на эти даты")

    _, free = free_units(db, equipment.id, data.start_date, data.end_date)
    if not free:
        raise HTTPException(status.HTTP_409_CONFLICT, "На выбранные даты всё оборудование занято")

    booking = Booking(
        user_id=user.id,
        equipment_id=equipment.id,
        start_date=data.start_date,
        end_date=data.end_date,
        user_comment=data.user_comment,
        status=BookingStatus.PENDING,
    )
    add_history(booking, None, BookingStatus.PENDING, user.id)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def approve_booking(db: Session, booking: Booking, admin: User, comment: Optional[str]) -> Booking:
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status.HTTP_409_CONFLICT, "Одобрить можно только заявку в статусе «на рассмотрении»")

    # Свободный экземпляр проверяем заново: пока заявка ждала, его могли занять
    _, free = free_units(db, booking.equipment_id, booking.start_date, booking.end_date)
    if not free:
        raise HTTPException(status.HTTP_409_CONFLICT, "Нет свободных экземпляров на эти даты")

    old_status = booking.status
    booking.unit_id = free[0].id
    booking.status = BookingStatus.APPROVED
    booking.decided_by = admin.id
    booking.decided_at = datetime.utcnow()
    booking.admin_comment = comment
    add_history(booking, old_status, BookingStatus.APPROVED, admin.id, comment)
    db.commit()
    db.refresh(booking)
    return booking


def reject_booking(db: Session, booking: Booking, admin: User, comment: Optional[str]) -> Booking:
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status.HTTP_409_CONFLICT, "Отклонить можно только заявку в статусе «на рассмотрении»")

    old_status = booking.status
    booking.status = BookingStatus.REJECTED
    booking.decided_by = admin.id
    booking.decided_at = datetime.utcnow()
    booking.admin_comment = comment
    add_history(booking, old_status, BookingStatus.REJECTED, admin.id, comment)
    db.commit()
    db.refresh(booking)
    return booking


def cancel_booking(db: Session, booking: Booking, user: User) -> Booking:
    if booking.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Это не ваша заявка")
    if booking.status not in CANCELLABLE_STATUSES:
        raise HTTPException(status.HTTP_409_CONFLICT, "Эту заявку уже нельзя отменить")

    old_status = booking.status
    booking.status = BookingStatus.CANCELLED
    add_history(booking, old_status, BookingStatus.CANCELLED, user.id)
    db.commit()
    db.refresh(booking)
    return booking
