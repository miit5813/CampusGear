from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Equipment
from app.models.enums import UnitStatus
from app.schemas.equipment import EquipmentDetail, EquipmentListItem

router = APIRouter(prefix="/api/equipment", tags=["Каталог"])

UNAVAILABLE_STATUSES = (UnitStatus.MAINTENANCE, UnitStatus.WRITTEN_OFF)


def _load_options():
    return (
        selectinload(Equipment.category),
        selectinload(Equipment.terms),
        selectinload(Equipment.photos),
        selectinload(Equipment.units),
    )


def _to_dict(equipment: Equipment) -> dict:
    main_photo = next((p for p in equipment.photos if p.is_main), None)
    if main_photo is None and equipment.photos:
        main_photo = equipment.photos[0]

    units_total = sum(1 for unit in equipment.units if unit.status not in UNAVAILABLE_STATUSES)

    return {
        "id": equipment.id,
        "name": equipment.name,
        "manufacturer": equipment.manufacturer,
        "description": equipment.description,
        "category": equipment.category,
        "terms": equipment.terms,
        "main_photo_url": main_photo.url if main_photo else None,
        "units_total": units_total,
        "photos": equipment.photos,
    }


@router.get("", response_model=list[EquipmentListItem], summary="Каталог оборудования")
def list_equipment(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = select(Equipment).where(Equipment.is_active.is_(True)).options(*_load_options())

    if category_id is not None:
        query = query.where(Equipment.category_id == category_id)
    if search:
        query = query.where(Equipment.name.ilike(f"%{search}%"))

    items = db.scalars(query.order_by(Equipment.name)).all()
    return [_to_dict(item) for item in items]


@router.get("/{equipment_id}", response_model=EquipmentDetail, summary="Карточка устройства")
def get_equipment(equipment_id: int, db: Session = Depends(get_db)):
    query = (
        select(Equipment)
        .where(Equipment.id == equipment_id, Equipment.is_active.is_(True))
        .options(*_load_options())
    )
    equipment = db.scalar(query)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")
    return _to_dict(equipment)
