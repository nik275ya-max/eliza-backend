from fastapi import FastAPI, Depends, Request, Form
from fastapi_admin.app import app as fastapi_admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Model, Field
from fastapi_admin.widgets import displays, inputs
from sqlalchemy.orm import Session
from starlette.admin import Admin

from app.core.database import get_db, engine, Base
from app.models.license import LicenseKey, AdminUser
from app.core.config import settings
from app.core.security import get_password_hash


# Создаём таблицы
Base.metadata.create_all(bind=engine)


# Инициализация админ-панели
admin = Admin(
    engine=engine,
    title="Eliza Admin",
    logo_url="https://via.placeholder.com/100x100?text=E",
    templates_dir="templates",
)


class LicenseKeyResource(Model):
    __tablename__ = LicenseKey.__tablename__
    __label__ = "Лицензионные ключи"
    
    id = Field(display=displays.Display(), input_=inputs.Number())
    key = Field(display=displays.Display(), input_=inputs.Text())
    is_activated = Field(display=displays.Boolean(), input_=inputs.Boolean())
    activation_count = Field(display=displays.Display(), input_=inputs.Number())
    max_activations = Field(display=displays.Display(), input_=inputs.Number())
    created_at = Field(display=displays.DateTime())


class AdminUserResource(Model):
    __tablename__ = AdminUser.__tablename__
    __label__ = "Администраторы"
    
    id = Field(display=displays.Display(), input_=inputs.Number())
    username = Field(display=displays.Display(), input_=inputs.Text())
    email = Field(display=displays.Display(), input_=inputs.Email())
    is_active = Field(display=displays.Boolean(), input_=inputs.Boolean())
    hashed_password = Field(display=displays.Display(), input_=inputs.Password())


# Регистрация ресурсов
admin.add_resource(LicenseKeyResource)
admin.add_resource(AdminUserResource)


def init_admin(app: FastAPI):
    """Инициализация админ-панели"""
    
    # Создаём администратора по умолчанию
    db = SessionLocal()
    try:
        admin_user = db.query(AdminUser).filter(
            AdminUser.username == settings.ADMIN_USERNAME
        ).first()
        
        if not admin_user:
            admin_user = AdminUser(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()
    
    # Монтируем админ-панель
    admin.mount_to(app)
