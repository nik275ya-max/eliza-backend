from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# License Schemas
class LicenseActivateRequest(BaseModel):
    key: str = Field(..., min_length=22, max_length=26, description="Лицензионный ключ")


class LicenseActivateResponse(BaseModel):
    valid: bool
    activated: Optional[bool] = None
    already_activated: Optional[bool] = None
    activation_count: Optional[int] = None
    max_activations: Optional[int] = None
    expires_formatted: Optional[str] = None
    error: Optional[str] = None


class LicenseKeyResponse(BaseModel):
    id: int
    key: str
    is_activated: bool
    activation_count: int
    max_activations: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LicenseKeyCreate(BaseModel):
    key: str
    max_activations: int = 1


class LicenseKeyUpdate(BaseModel):
    is_activated: Optional[bool] = None
    activation_count: Optional[int] = None
    max_activations: Optional[int] = None


# Admin Schemas
class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    
    class Config:
        from_attributes = True


# Stats Schema
class StatsResponse(BaseModel):
    total_keys: int
    activated_keys: int
    active_keys: int
    total_activations: int
