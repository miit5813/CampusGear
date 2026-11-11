from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schemas.equipment import CategoryOut

router = APIRouter(prefix="/api/categories", tags=["Каталог"])


@router.get("", response_model=list[CategoryOut], summary="Список категорий")
def list_categories(db: Session = Depends(get_db)):
    categories = db.scalars(select(Category).order_by(Category.name)).all()
    return categories