from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import AllowedFor


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None


class RentalTermOut(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    max_days: int
    deposit: float
    fine_per_day: float
    allowed_for: AllowedFor
    requirements: Optional[str] = None


class PhotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    is_main: bool
    sort_order: int


class EquipmentListItem(BaseModel):

    id: int
    name: str
    manufacturer: Optional[str] = None
    description: Optional[str] = None
    category: CategoryOut
    terms: Optional[RentalTermOut] = None
    main_photo_url: Optional[str] = None
    units_total: int


class EquipmentDetail(EquipmentListItem):

    photos: list[PhotoOut] = []
