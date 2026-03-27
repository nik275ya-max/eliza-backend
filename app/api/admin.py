from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

from app.core.database import get_db
from app.schemas.license import AdminLoginRequest, AdminTokenResponse, AdminUserResponse
from app.models.license import AdminUser
from app.core.security import verify_password, create_access_token
from app.core.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> AdminUser:
    """Получение текущего администратора"""
    from app.core.security import decode_access_token
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Неверный токен")
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Неверный токен")
    
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if admin is None:
        raise HTTPException(status_code=404, detail="Администратор не найден")
    
    return admin


@router.post("/login", response_model=AdminTokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Вход администратора"""
    admin = db.query(AdminUser).filter(AdminUser.username == form_data.username).first()
    
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username},
        expires_delta=access_token_expires,
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=AdminUserResponse)
async def get_current_admin_info(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Информация о текущем администраторе"""
    return current_admin
