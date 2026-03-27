from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class LicenseKey(Base):
    """Модель лицензионного ключа"""
    
    __tablename__ = "license_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(26), unique=True, index=True, nullable=False)
    is_activated = Column(Boolean, default=False)
    activation_count = Column(Integer, default=0)
    max_activations = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<LicenseKey {self.key}>"


class AdminUser(Base):
    """Модель администратора"""
    
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AdminUser {self.username}>"
