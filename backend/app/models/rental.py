from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import FineStatus, FineType, UnitCondition, enum_column


class Handover(Base):
    """Выдача оборудования с отметкой о состоянии."""

    __tablename__ = "handovers"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), unique=True
    )
    unit_id: Mapped[int] = mapped_column(ForeignKey("equipment_units.id", ondelete="RESTRICT"))
    issued_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    issued_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    condition_on_issue: Mapped[UnitCondition] = mapped_column(enum_column(UnitCondition))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    booking: Mapped["Booking"] = relationship(back_populates="handover")


class Return(Base):
    """Возврат оборудования с проверкой состояния."""

    __tablename__ = "returns"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), unique=True
    )
    accepted_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    returned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    condition_on_return: Mapped[UnitCondition] = mapped_column(enum_column(UnitCondition))
    has_damage: Mapped[bool] = mapped_column(default=False, server_default=false())
    damage_description: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    booking: Mapped["Booking"] = relationship(back_populates="return_record")


class Fine(Base):
    """Штраф за просрочку, повреждение или утерю."""

    __tablename__ = "fines"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    fine_type: Mapped[FineType] = mapped_column(enum_column(FineType))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    days_overdue: Mapped[Optional[int]]
    status: Mapped[FineStatus] = mapped_column(
        enum_column(FineStatus), default=FineStatus.UNPAID, server_default=FineStatus.UNPAID.value
    )
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    booking: Mapped["Booking"] = relationship(back_populates="fines")
    user: Mapped["User"] = relationship(back_populates="fines")
