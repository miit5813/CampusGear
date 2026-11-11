from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func, false, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import AllowedFor, UnitCondition, UnitStatus, enum_column


class Category(Base):
    """Категория оборудования: проекторы, камеры, микрофоны и т. д."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    equipment: Mapped[list["Equipment"]] = relationship(back_populates="category")


class Equipment(Base):
    """Модель оборудования (карточка в каталоге). Конкретные экземпляры лежат в equipment_units."""

    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[Optional[str]] = mapped_column(Text)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    category: Mapped["Category"] = relationship(back_populates="equipment")
    units: Mapped[list["EquipmentUnit"]] = relationship(back_populates="equipment")
    photos: Mapped[list["EquipmentPhoto"]] = relationship(
        back_populates="equipment", order_by="EquipmentPhoto.sort_order"
    )
    terms: Mapped[Optional["RentalTerm"]] = relationship(back_populates="equipment", uselist=False)
    bookings: Mapped[list["Booking"]] = relationship(back_populates="equipment")
    waitlist_entries: Mapped[list["WaitlistEntry"]] = relationship(back_populates="equipment")


class RentalTerm(Base):
    """Условия аренды: максимальный срок, залог, штраф за день просрочки, требования."""

    __tablename__ = "rental_terms"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id", ondelete="CASCADE"), unique=True
    )
    max_days: Mapped[int] = mapped_column(default=7, server_default="7")
    deposit: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, server_default="0")
    fine_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, server_default="0")
    allowed_for: Mapped[AllowedFor] = mapped_column(
        enum_column(AllowedFor), default=AllowedFor.ALL, server_default=AllowedFor.ALL.value
    )
    requirements: Mapped[Optional[str]] = mapped_column(Text)

    equipment: Mapped["Equipment"] = relationship(back_populates="terms")


class EquipmentUnit(Base):
    """Конкретный экземпляр оборудования с инвентарным номером."""

    __tablename__ = "equipment_units"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id", ondelete="CASCADE"))
    inventory_number: Mapped[str] = mapped_column(String(50), unique=True)
    condition: Mapped[UnitCondition] = mapped_column(
        enum_column(UnitCondition), default=UnitCondition.GOOD, server_default=UnitCondition.GOOD.value
    )
    status: Mapped[UnitStatus] = mapped_column(
        enum_column(UnitStatus), default=UnitStatus.AVAILABLE, server_default=UnitStatus.AVAILABLE.value
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    equipment: Mapped["Equipment"] = relationship(back_populates="units")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="unit")


class EquipmentPhoto(Base):
    """Фотографии оборудования."""

    __tablename__ = "equipment_photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(500))
    is_main: Mapped[bool] = mapped_column(default=False, server_default=false())
    sort_order: Mapped[int] = mapped_column(default=0, server_default="0")

    equipment: Mapped["Equipment"] = relationship(back_populates="photos")
