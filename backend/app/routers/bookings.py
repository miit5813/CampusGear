from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Booking, Equipment, User
from app.models.enums import BookingStatus
from app.schemas.booking import AvailabilityOut, BookingCreate, BookingDecision, BookingOut
from app.services import booking as booking_service

router = APIRouter(prefix="/api/bookings", tags=["Заявки"])


def _with_relations(query):
    """Сразу подгружаем оборудование, пользователя и экземпляр."""
    return query.options(
        selectinload(Booking.equipment),
        selectinload(Booking.user),
        selectinload(Booking.unit),
    )


def _get_or_404(db: Session, booking_id: int) -> Booking:
    booking = db.scalar(_with_relations(select(Booking).where(Booking.id == booking_id)))
    if booking is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return booking


@router.get("/availability", response_model=AvailabilityOut, summary="Доступность оборудования на период")
def availability(equipment_id: int, start_date: date, end_date: date, db: Session = Depends(get_db)):
    booking_service.validate_period(start_date, end_date)
    equipment = db.scalar(select(Equipment).where(Equipment.id == equipment_id, Equipment.is_active.is_(True)))
    if equipment is None:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")

    units, free = booking_service.free_units(db, equipment_id, start_date, end_date)
    return AvailabilityOut(
        equipment_id=equipment_id,
        start_date=start_date,
        end_date=end_date,
        units_total=len(units),
        units_free=len(free),
        available=len(free) > 0,
    )


@router.post("", response_model=BookingOut, status_code=201, summary="Подать заявку на аренду")
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = booking_service.create_booking(db, current_user, data)
    return _get_or_404(db, booking.id)


@router.get("/my", response_model=list[BookingOut], summary="Мои заявки")
def my_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = _with_relations(select(Booking).where(Booking.user_id == current_user.id))
    return db.scalars(query.order_by(Booking.created_at.desc(), Booking.id.desc())).all()


@router.post("/{booking_id}/cancel", response_model=BookingOut, summary="Отменить свою заявку")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = booking_service.cancel_booking(db, _get_or_404(db, booking_id), current_user)
    return _get_or_404(db, booking.id)


@router.get("", response_model=list[BookingOut], summary="Все заявки (администратор)")
def list_bookings(
    status: Optional[BookingStatus] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    query = _with_relations(select(Booking))
    if status is not None:
        query = query.where(Booking.status == status)
    return db.scalars(query.order_by(Booking.created_at.desc(), Booking.id.desc())).all()


@router.post("/{booking_id}/approve", response_model=BookingOut, summary="Одобрить заявку (администратор)")
def approve_booking(
    booking_id: int,
    data: Optional[BookingDecision] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    comment = data.admin_comment if data else None
    booking = booking_service.approve_booking(db, _get_or_404(db, booking_id), admin, comment)
    return _get_or_404(db, booking.id)


@router.post("/{booking_id}/reject", response_model=BookingOut, summary="Отклонить заявку (администратор)")
def reject_booking(
    booking_id: int,
    data: Optional[BookingDecision] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    comment = data.admin_comment if data else None
    booking = booking_service.reject_booking(db, _get_or_404(db, booking_id), admin, comment)
    return _get_or_404(db, booking.id)
