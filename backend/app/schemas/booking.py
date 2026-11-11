from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BookingStatus


class BookingCreate(BaseModel):
    """Данные заявки на аренду."""

    equipment_id: int
    start_date: date
    end_date: date
    user_comment: Optional[str] = Field(default=None, max_length=500)


class BookingDecision(BaseModel):
    """Комментарий администратора при одобрении или отклонении."""

    admin_comment: Optional[str] = Field(default=None, max_length=500)


class EquipmentShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class UserShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class UnitShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventory_number: str


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: BookingStatus
    start_date: date
    end_date: date
    user_comment: Optional[str] = None
    admin_comment: Optional[str] = None
    created_at: datetime
    equipment: EquipmentShort
    user: UserShort
    unit: Optional[UnitShort] = None


class AvailabilityOut(BaseModel):
    """Сколько экземпляров свободно на выбранный период."""

    equipment_id: int
    start_date: date
    end_date: date
    units_total: int
    units_free: int
    available: bool
