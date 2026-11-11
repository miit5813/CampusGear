"""Импорт всех моделей нужен, чтобы Alembic видел все таблицы."""
from app.models.booking import Booking, BookingStatusHistory, WaitlistEntry
from app.models.equipment import Category, Equipment, EquipmentPhoto, EquipmentUnit, RentalTerm
from app.models.notification import AuditLog, Notification
from app.models.rental import Fine, Handover, Return
from app.models.user import User

__all__ = [
    "AuditLog",
    "Booking",
    "BookingStatusHistory",
    "Category",
    "Equipment",
    "EquipmentPhoto",
    "EquipmentUnit",
    "Fine",
    "Handover",
    "Notification",
    "RentalTerm",
    "Return",
    "User",
    "WaitlistEntry",
]
