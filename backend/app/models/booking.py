from datetime import date, datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import BookingStatus, WaitlistStatus, enum_column


class Booking(Base):
    """Заявка на аренду. Конкретный экземпляр (unit_id) назначается при одобрении."""

    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="ck_bookings_dates"),
        Index("ix_bookings_equipment_period", "equipment_id", "start_date", "end_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id", ondelete="RESTRICT"))
    unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("equipment_units.id", ondelete="SET NULL")
    )
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[BookingStatus] = mapped_column(
        enum_column(BookingStatus),
        default=BookingStatus.PENDING,
        server_default=BookingStatus.PENDING.value,
    )
    user_comment: Mapped[Optional[str]] = mapped_column(Text)
    admin_comment: Mapped[Optional[str]] = mapped_column(Text)
    decided_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="bookings", foreign_keys=[user_id])
    decider: Mapped[Optional["User"]] = relationship(foreign_keys=[decided_by])
    equipment: Mapped["Equipment"] = relationship(back_populates="bookings")
    unit: Mapped[Optional["EquipmentUnit"]] = relationship(back_populates="bookings")
    status_history: Mapped[list["BookingStatusHistory"]] = relationship(
        back_populates="booking", order_by="BookingStatusHistory.changed_at"
    )
    handover: Mapped[Optional["Handover"]] = relationship(back_populates="booking", uselist=False)
    return_record: Mapped[Optional["Return"]] = relationship(back_populates="booking", uselist=False)
    fines: Mapped[list["Fine"]] = relationship(back_populates="booking")


class BookingStatusHistory(Base):
    """Журнал смены статусов заявки."""

    __tablename__ = "booking_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"))
    old_status: Mapped[Optional[str]] = mapped_column(String(30))
    new_status: Mapped[str] = mapped_column(String(30))
    changed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    booking: Mapped["Booking"] = relationship(back_populates="status_history")


class WaitlistEntry(Base):
    """Очередь ожидания на занятое оборудование."""

    __tablename__ = "waitlist_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id", ondelete="CASCADE"))
    desired_start: Mapped[date] = mapped_column(Date)
    desired_end: Mapped[date] = mapped_column(Date)
    status: Mapped[WaitlistStatus] = mapped_column(
        enum_column(WaitlistStatus),
        default=WaitlistStatus.WAITING,
        server_default=WaitlistStatus.WAITING.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    notified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="waitlist_entries")
    equipment: Mapped["Equipment"] = relationship(back_populates="waitlist_entries")
