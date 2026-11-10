from pydantic import BaseModel, EmailStr

from app.schemas.user import UserOut


class LoginRequest(BaseModel):
    """Данные формы входа."""

    email: EmailStr
    password: str


class TokenOut(BaseModel):
    """Ответ на успешный вход: токен и данные пользователя."""

    access_token: str
    token_type: str = "bearer"
    user: UserOut
