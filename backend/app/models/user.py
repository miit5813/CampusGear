from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, func, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import UserRole, UserType, enum_column


class User(Base):
    """Пользователь сервиса: студент, сотрудник или администратор."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        enum_column(UserRole), default=UserRole.USER, server_default=UserRole.USER.value
    )
    user_type: Mapped[UserType] = mapped_column(
        enum_column(UserType), default=UserType.STUDENT, server_default=UserType.STUDENT.value
    )
    group_or_department: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(30))
    is_blocked: Mapped[bool] = mapped_column(default=False, server_default=false())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="user", foreign_keys="Booking.user_id"
    )
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    fines: Mapped[list["Fine"]] = relationship(back_populates="user")
    waitlist_entries: Mapped[list["WaitlistEntry"]] = relationship(back_populates="user")
