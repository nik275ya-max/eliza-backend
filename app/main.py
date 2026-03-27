from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api import licenses, admin as admin_router
from app.models.license import AdminUser
from app.core.security import get_password_hash


@asynccontextmanager
async def lifespan(app: FastAPI):
    """События запуска и остановки"""
    # Создаём таблицы
    Base.metadata.create_all(bind=engine)

    # Создаём администратора по умолчанию
    try:
        db = SessionLocal()
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
            print(f"✓ Администратор создан: {settings.ADMIN_USERNAME}")
    except Exception as e:
        print(f"⚠ Ошибка создания администратора: {e}")
    finally:
        db.close()

    yield


# Создание приложения
app = FastAPI(
    title="Eliza License API",
    description="API для управления лицензиями",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(licenses.router)
app.include_router(admin_router.router)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Eliza License API",
        "docs": "/docs",
        "admin_docs": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Проверка работоспособности"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
