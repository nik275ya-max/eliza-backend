from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.license import (
    LicenseActivateRequest,
    LicenseActivateResponse,
    LicenseKeyResponse,
    LicenseKeyCreate,
    LicenseKeyUpdate,
    StatsResponse,
)
from app.services.license import license_service
from app.core.security import verify_password, get_password_hash
from app.models.license import AdminUser

router = APIRouter(prefix="/api/v1/license", tags=["Licenses"])


@router.post("/activate", response_model=LicenseActivateResponse)
async def activate_license(request: LicenseActivateRequest, db: Session = Depends(get_db)):
    """Активация лицензионного ключа"""
    key = request.key.strip().upper()
    
    # Валидация формата
    validation = license_service.validate_key_format(key)
    if not validation["valid"]:
        return LicenseActivateResponse(
            valid=False,
            error=validation["error"],
            expires_formatted=validation.get("expires_formatted"),
        )
    
    # Проверка ключа в БД
    db_key = license_service.get_by_key(db, key)
    
    if not db_key:
        return LicenseActivateResponse(
            valid=False,
            error="Ключ не найден в базе данных",
            expires_formatted=validation["expires_formatted"],
        )
    
    # Проверка лимита активаций
    if db_key.is_activated and db_key.activation_count >= db_key.max_activations:
        return LicenseActivateResponse(
            valid=True,
            already_activated=True,
            activation_count=db_key.activation_count,
            max_activations=db_key.max_activations,
            expires_formatted=validation["expires_formatted"],
        )
    
    # Активация
    license_service.activate_key(db, db_key)
    
    return LicenseActivateResponse(
        valid=True,
        activated=True,
        activation_count=db_key.activation_count,
        max_activations=db_key.max_activations,
        expires_formatted=validation["expires_formatted"],
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Получение статистики по лицензиям"""
    stats = license_service.get_stats(db)
    return StatsResponse(**stats)


@router.get("/", response_model=List[LicenseKeyResponse])
async def get_all_keys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получение всех лицензионных ключей"""
    keys = license_service.get_all_keys(db, skip=skip, limit=limit)
    return keys


@router.post("/", response_model=LicenseKeyResponse)
async def create_key(
    key_data: LicenseKeyCreate,
    db: Session = Depends(get_db)
):
    """Создание нового лицензионного ключа"""
    # Проверка существования
    existing = license_service.get_by_key(db, key_data.key)
    if existing:
        raise HTTPException(status_code=400, detail="Ключ уже существует")
    
    return license_service.create_key(db, key_data.key, key_data.max_activations)


@router.delete("/{key_id}")
async def delete_key(key_id: int, db: Session = Depends(get_db)):
    """Удаление лицензионного ключа"""
    if not license_service.delete_key(db, key_id):
        raise HTTPException(status_code=404, detail="Ключ не найден")
    return {"message": "Ключ удалён"}
