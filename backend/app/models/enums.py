import enum

from sqlalchemy import Enum


def enum_column(enum_class: type[enum.Enum]) -> Enum:
    """Хранит значения enum в БД как обычные строки (VARCHAR), без нативных типов PostgreSQL."""
    return Enum(
        enum_class,
        native_enum=False,
        length=30,
        values_callable=lambda members: [member.value for member in members],
    )


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class UserType(str, enum.Enum):
    STUDENT = "student"
    EMPLOYEE = "employee"


class AllowedFor(str, enum.Enum):
    """Кому разрешена аренда оборудования."""
    ALL = "all"
    STUDENT = "student"
    EMPLOYEE = "employee"


class UnitCondition(str, enum.Enum):
    NEW = "new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class UnitStatus(str, enum.Enum):
    AVAILABLE = "available"
    ISSUED = "issued"
    MAINTENANCE = "maintenance"
    WRITTEN_OFF = "written_off"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    ISSUED = "issued"
    RETURNED = "returned"
    OVERDUE = "overdue"


class WaitlistStatus(str, enum.Enum):
    WAITING = "waiting"
    NOTIFIED = "notified"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class FineType(str, enum.Enum):
    OVERDUE = "overdue"
    DAMAGE = "damage"
    LOSS = "loss"


class FineStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    CANCELLED = "cancelled"


class NotificationType(str, enum.Enum):
    BOOKING_STATUS = "booking_status"
    RENTAL_ENDING = "rental_ending"
    OVERDUE = "overdue"
    WAITLIST_AVAILABLE = "waitlist_available"
    FINE = "fine"
