from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

from app.core.database import get_db, engine, Base
from app.models.license import AdminUser
from app.core.config import settings
from app.admin.views import LicenseKeyAdmin, AdminUserAdmin


# Хеш паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 для проверки токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login", auto_error=False)

# Секретный ключ для JWT
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # Токен на 7 дней
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_admin(request: Request, db: Session = Depends(get_db)):
    """Получение текущего администратора из токена"""
    token = request.cookies.get("admin_token")
    
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
        
        admin = db.query(AdminUser).filter(AdminUser.username == username).first()
        return admin
    except JWTError:
        return None


def admin_required(request: Request, db: Session = Depends(get_db)):
    """Требует авторизации администратора"""
    admin = get_current_admin(request, db)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/admin/login"}
        )
    return admin


# Создание таблиц
Base.metadata.create_all(bind=engine)

# Создание администратора по умолчанию
db_session = Session(engine)
try:
    admin_user = db_session.query(AdminUser).filter(
        AdminUser.username == settings.ADMIN_USERNAME
    ).first()
    
    if not admin_user:
        admin_user = AdminUser(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=pwd_context.hash(settings.ADMIN_PASSWORD),
            is_active=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        print(f"✓ Администратор создан: {settings.ADMIN_USERNAME}")
finally:
    db_session.close()


# Создание админ-панели
admin_app = FastAPI(title="Eliza Admin")

admin = Admin(
    app=admin_app,
    engine=engine,
    title="Eliza Admin",
    logo_url="https://via.placeholder.com/100x100?text=E",
    base_url="/admin",
)

admin.add_view(LicenseKeyAdmin)
admin.add_view(AdminUserAdmin)


@admin_app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа"""
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Вход в админку - Eliza</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .login-card {
                background: rgba(45, 55, 72, 0.9);
                border: 2px solid #4a5568;
                border-radius: 12px;
                padding: 2rem;
                width: 100%;
                max-width: 400px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            }
            .login-title {
                color: #e6e6fa;
                text-align: center;
                margin-bottom: 2rem;
                font-family: 'Georgia', serif;
                letter-spacing: 0.1em;
            }
            .form-control {
                background: rgba(45, 55, 72, 0.8);
                border: 2px solid #4a5568;
                color: #e6e6fa;
            }
            .form-control:focus {
                background: rgba(45, 55, 72, 0.9);
                border-color: #9f7aea;
                color: #e6e6fa;
                box-shadow: 0 0 0 3px rgba(159, 122, 234, 0.2);
            }
            .btn-login {
                background: linear-gradient(135deg, #9f7aea 0%, #7c3aed 100%);
                border: none;
                color: white;
                padding: 0.75rem;
                font-weight: 500;
                width: 100%;
            }
            .btn-login:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(159, 122, 234, 0.4);
            }
            .error-message {
                background: rgba(252, 129, 129, 0.1);
                border: 1px solid #fc8181;
                color: #fc8181;
                padding: 0.75rem;
                border-radius: 6px;
                margin-bottom: 1rem;
            }
            label {
                color: #e6e6fa;
                margin-bottom: 0.5rem;
            }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h1 class="login-title">🔐 Eliza Admin</h1>
            
            <div id="error-message" class="error-message" style="display: none;"></div>
            
            <form id="login-form">
                <div class="mb-3">
                    <label for="password" class="form-label">Пароль администратора</label>
                    <input type="password" class="form-control" id="password" required autofocus>
                </div>
                <button type="submit" class="btn btn-login">Войти</button>
            </form>
        </div>
        
        <script>
            document.getElementById('login-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const password = document.getElementById('password').value;
                const errorDiv = document.getElementById('error-message');
                
                try {
                    const response = await fetch('/admin/authenticate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: 'password=' + encodeURIComponent(password)
                    });
                    
                    if (response.ok) {
                        window.location.href = '/admin/';
                    } else {
                        const data = await response.json();
                        errorDiv.textContent = data.detail || 'Ошибка входа';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Ошибка соединения';
                    errorDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """


@admin_app.post("/authenticate")
async def authenticate(request: Request, password: str = Form(...), db: Session = Depends(get_db)):
    """Аутентификация по паролю"""
    # Получаем первого администратора (главного)
    admin = db.query(AdminUser).first()
    
    if not admin or not verify_password(password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт заблокирован"
        )
    
    # Создаём токен
    token = create_access_token(data={"sub": admin.username})
    
    # Перенаправляем в админку
    response = RedirectResponse(url="/admin/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    response.set_cookie(key="admin_token", value=token, httponly=True, max_age=604800)  # 7 дней
    return response


@admin_app.get("/logout")
async def logout():
    """Выход из админки"""
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    response.delete_cookie("admin_token")
    return response


# Монтируем SQLAdmin
admin.mount_to(admin_app)
