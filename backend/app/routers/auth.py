from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserOut
from app.security import hash_password, verify_password
from app.dependencies import get_current_user
from app.schemas.auth import LoginRequest, TokenOut
from app.tokens import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Авторизация"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    email = data.email.lower()
    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user:
        raise HTTPException(status_code =409, detail = "Пользователй с такой почтой уже существует") 
    password_hash = hash_password(data.password)
    user =User(full_name = data.full_name,
               email = email, 
               password_hash = password_hash,
               user_type = data.user_type, 
               group_or_department = data.group_or_department,
               phone = data.phone)
    db.add(user)
    db.commit()
    db.refresh(user)


@router.post("/login", response_model=TokenOut, summary="Вход в систему")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")

    token = create_access_token(user_id=user.id, role=user.role.value)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))



@router.get("/me", response_model=UserOut, summary="Текущий пользователь")
def me(current_user: User = Depends(get_current_user)):
    return current_user

