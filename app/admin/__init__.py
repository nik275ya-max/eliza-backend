from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

from app.core.database import get_db, engine, Base
from app.models.license import AdminUser, LicenseKey
from app.core.config import settings


# Хеш паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT настройки
SECRET_KEY = os.getenv("SECRET_KEY", "eliza-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    # bcrypt ограничивает пароль 72 байтами
    return pwd_context.hash(password[:72])


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_admin(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("admin_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
        admin = db.query(AdminUser).filter(AdminUser.username == username).first()
        return admin if admin and admin.is_active else None
    except JWTError:
        return None


def admin_required(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/admin/login"}
        )
    return admin


# ===== СТРАНИЦЫ =====

def get_login_html():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Вход в админку - Eliza</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .login-card {
                background: rgba(45, 55, 72, 0.95);
                border: 2px solid #4a5568;
                border-radius: 16px;
                padding: 2.5rem;
                width: 100%;
                max-width: 420px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
            }
            .login-title {
                color: #e6e6fa;
                text-align: center;
                margin-bottom: 0.5rem;
                font-family: 'Georgia', serif;
                font-size: 2rem;
            }
            .login-subtitle {
                color: #9999b3;
                text-align: center;
                margin-bottom: 2rem;
                font-size: 0.9rem;
            }
            .form-control {
                background: rgba(45, 55, 72, 0.8);
                border: 2px solid #4a5568;
                color: #e6e6fa;
                padding: 0.75rem 1rem;
                border-radius: 8px;
            }
            .form-control:focus {
                background: rgba(45, 55, 72, 0.9);
                border-color: #9f7aea;
                color: #e6e6fa;
                box-shadow: 0 0 0 3px rgba(159, 122, 234, 0.2);
            }
            .form-label {
                color: #e6e6fa;
                font-weight: 500;
                margin-bottom: 0.5rem;
            }
            .btn-login {
                background: linear-gradient(135deg, #9f7aea 0%, #7c3aed 100%);
                border: none;
                color: white;
                padding: 0.875rem;
                font-weight: 600;
                width: 100%;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            .btn-login:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 30px rgba(159, 122, 234, 0.5);
            }
            .error-message {
                background: rgba(252, 129, 129, 0.15);
                border: 1px solid #fc8181;
                color: #fc8181;
                padding: 0.875rem;
                border-radius: 8px;
                margin-bottom: 1.5rem;
                display: none;
            }
            .logo-icon {
                font-size: 3rem;
                color: #9f7aea;
                text-align: center;
                margin-bottom: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="login-card">
            <div class="logo-icon">
                <i class="bi bi-shield-lock"></i>
            </div>
            <h1 class="login-title">Eliza Admin</h1>
            <p class="login-subtitle">Панель управления лицензиями</p>
            
            <div id="error-message" class="error-message">
                <i class="bi bi-exclamation-triangle-fill"></i>
                <span id="error-text"></span>
            </div>
            
            <form id="login-form">
                <div class="mb-4">
                    <label for="password" class="form-label">
                        <i class="bi bi-key-fill"></i> Пароль администратора
                    </label>
                    <input type="password" class="form-control" id="password" 
                           placeholder="Введите пароль" required autofocus>
                </div>
                <button type="submit" class="btn btn-login">
                    <i class="bi bi-box-arrow-in-right"></i> Войти
                </button>
            </form>
        </div>
        
        <script>
            document.getElementById('login-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const password = document.getElementById('password').value;
                const errorDiv = document.getElementById('error-message');
                const errorText = document.getElementById('error-text');
                
                try {
                    const response = await fetch('/admin/authenticate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: 'password=' + encodeURIComponent(password)
                    });
                    
                    if (response.ok) {
                        window.location.href = '/admin/dashboard';
                    } else {
                        const data = await response.json();
                        errorText.textContent = data.detail || 'Неверный пароль';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorText.textContent = 'Ошибка соединения с сервером';
                    errorDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """


def get_dashboard_html(admin: AdminUser, db: Session):
    from sqlalchemy import func
    
    # Получаем статистику
    total_keys = db.query(LicenseKey).count()
    activated_keys = db.query(LicenseKey).filter(LicenseKey.is_activated == True).count()
    active_keys = db.query(LicenseKey).filter(
        LicenseKey.is_activated == True,
        LicenseKey.activation_count < LicenseKey.max_activations
    ).count()
    total_activations = db.query(LicenseKey.activation_count).with_entities(
        func.sum(LicenseKey.activation_count)
    ).scalar() or 0
    
    # Получаем последние ключи
    recent_keys = db.query(LicenseKey).order_by(LicenseKey.created_at.desc()).limit(10).all()
    
    rows_html = ""
    for k in recent_keys:
        status_badge = "badge-activated" if k.is_activated else "badge-not-activated"
        status_text = "✓ Активирован" if k.is_activated else "✗ Не активирован"
        date_str = k.created_at.strftime("%d.%m.%Y %H:%M") if k.created_at else "-"
        rows_html += f"""
        <tr>
            <td><code>{k.key}</code></td>
            <td><span class="badge {status_badge}">{status_text}</span></td>
            <td>{k.activation_count}</td>
            <td>{k.max_activations}</td>
            <td>{date_str}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Панель управления - Eliza Admin</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            :root {{
                --bg-primary: #1a1a2e;
                --bg-secondary: #16213e;
                --bg-card: #1f2940;
                --text-primary: #e6e6fa;
                --text-secondary: #9999b3;
                --accent: #9f7aea;
                --success: #68d391;
                --warning: #f6ad55;
                --danger: #fc8181;
            }}
            body {{
                background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
                min-height: 100vh;
                color: var(--text-primary);
            }}
            .sidebar {{
                background: rgba(26, 26, 46, 0.95);
                border-right: 1px solid #4a5568;
                min-height: 100vh;
                padding: 1.5rem;
            }}
            .sidebar-brand {{
                color: var(--accent);
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 2rem;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }}
            .nav-link {{
                color: var(--text-secondary);
                padding: 0.875rem 1rem;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                transition: all 0.3s ease;
            }}
            .nav-link:hover, .nav-link.active {{
                background: rgba(159, 122, 234, 0.15);
                color: var(--accent);
            }}
            .nav-link i {{
                margin-right: 0.75rem;
            }}
            .main-content {{
                padding: 2rem;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 2rem;
                padding-bottom: 1.5rem;
                border-bottom: 1px solid #4a5568;
            }}
            .header-title {{
                font-size: 1.75rem;
                font-weight: 600;
                color: var(--text-primary);
            }}
            .user-menu {{
                display: flex;
                align-items: center;
                gap: 1rem;
            }}
            .btn-logout {{
                background: rgba(252, 129, 129, 0.15);
                border: 1px solid var(--danger);
                color: var(--danger);
                padding: 0.5rem 1rem;
                border-radius: 8px;
                transition: all 0.3s ease;
            }}
            .btn-logout:hover {{
                background: rgba(252, 129, 129, 0.25);
                color: var(--danger);
            }}
            .stat-card {{
                background: var(--bg-card);
                border: 1px solid #4a5568;
                border-radius: 12px;
                padding: 1.5rem;
                height: 100%;
            }}
            .stat-card-icon {{
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }}
            .stat-card-value {{
                font-size: 2rem;
                font-weight: 700;
                color: var(--text-primary);
            }}
            .stat-card-label {{
                color: var(--text-secondary);
                font-size: 0.9rem;
            }}
            .table-container {{
                background: var(--bg-card);
                border: 1px solid #4a5568;
                border-radius: 12px;
                padding: 1.5rem;
            }}
            .table {{
                color: var(--text-primary);
            }}
            .table thead th {{
                border-bottom: 2px solid #4a5568;
                color: var(--text-secondary);
                font-weight: 600;
            }}
            .table tbody td {{
                border-color: #4a5568;
                vertical-align: middle;
            }}
            .badge-activated {{
                background: rgba(104, 211, 145, 0.15);
                color: var(--success);
                border: 1px solid var(--success);
            }}
            .badge-not-activated {{
                background: rgba(252, 129, 129, 0.15);
                color: var(--danger);
                border: 1px solid var(--danger);
            }}
            .btn-create {{
                background: linear-gradient(135deg, var(--accent) 0%, #7c3aed 100%);
                border: none;
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                font-weight: 500;
            }}
            .btn-create:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(159, 122, 234, 0.4);
            }}
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <!-- Sidebar -->
                <div class="col-md-2 sidebar">
                    <div class="sidebar-brand">
                        <i class="bi bi-shield-lock"></i>
                        Eliza Admin
                    </div>
                    <nav class="nav flex-column">
                        <a class="nav-link active" href="/admin/dashboard">
                            <i class="bi bi-speedometer2"></i> Обзор
                        </a>
                        <a class="nav-link" href="/admin/licensekey/">
                            <i class="bi bi-key"></i> Лицензии
                        </a>
                        <a class="nav-link" href="/admin/adminuser/">
                            <i class="bi bi-people"></i> Администраторы
                        </a>
                    </nav>
                </div>
                
                <!-- Main Content -->
                <div class="col-md-10 main-content">
                    <div class="header">
                        <h1 class="header-title">Панель управления</h1>
                        <div class="user-menu">
                            <span><i class="bi bi-person-circle"></i> {admin.username}</span>
                            <a href="/admin/logout" class="btn btn-logout">
                                <i class="bi bi-box-arrow-right"></i> Выйти
                            </a>
                        </div>
                    </div>
                    
                    <!-- Stats -->
                    <div class="row g-4 mb-4">
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-card-icon" style="color: var(--accent);">
                                    <i class="bi bi-key-fill"></i>
                                </div>
                                <div class="stat-card-value">{total_keys}</div>
                                <div class="stat-card-label">Всего ключей</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-card-icon" style="color: var(--success);">
                                    <i class="bi bi-check-circle-fill"></i>
                                </div>
                                <div class="stat-card-value">{activated_keys}</div>
                                <div class="stat-card-label">Активировано</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-card-icon" style="color: var(--warning);">
                                    <i class="bi bi-activity"></i>
                                </div>
                                <div class="stat-card-value">{active_keys}</div>
                                <div class="stat-card-label">Активных</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-card-icon" style="color: var(--danger);">
                                    <i class="bi bi-lightning-fill"></i>
                                </div>
                                <div class="stat-card-value">{total_activations}</div>
                                <div class="stat-card-label">Всего активаций</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recent Keys -->
                    <div class="table-container">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h4><i class="bi bi-clock-history"></i> Последние ключи</h4>
                            <button class="btn btn-create" data-bs-toggle="modal" data-bs-target="#createKeyModal">
                                <i class="bi bi-plus-lg"></i> Создать ключ
                            </button>
                        </div>
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Ключ</th>
                                        <th>Статус</th>
                                        <th>Активаций</th>
                                        <th>Макс.</th>
                                        <th>Дата создания</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows_html}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- Modal для создания ключа -->
                    <div class="modal fade" id="createKeyModal" tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content" style="background: var(--bg-card); border: 1px solid #4a5568;">
                                <form method="POST" action="/admin/licensekey/create">
                                    <div class="modal-header" style="border-bottom: 1px solid #4a5568;">
                                        <h5 class="modal-title" style="color: var(--text-primary);">Создать ключ</h5>
                                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body">
                                        <div class="mb-3">
                                            <label class="form-label" style="color: var(--text-primary);">Лицензионный ключ</label>
                                            <input type="text" name="key" class="form-control" 
                                                   placeholder="ELIZA-YYYYMMDD-XXXX-XXXX" 
                                                   required style="text-transform: uppercase;"
                                                   id="keyInput">
                                            <small class="form-text" style="color: var(--text-secondary);">
                                                Формат: ELIZA-YYYYMMDD-XXXX-XXXX
                                            </small>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label" style="color: var(--text-primary);">Макс. активаций</label>
                                            <input type="number" name="max_activations" class="form-control" 
                                                   value="1" min="1" max="100">
                                        </div>
                                    </div>
                                    <div class="modal-footer" style="border-top: 1px solid #4a5568;">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                                        <button type="submit" class="btn btn-create">Создать</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Автоматическое приведение к верхнему регистру
            document.getElementById('keyInput').addEventListener('input', function(e) {
                this.value = this.value.toUpperCase();
            });
            
            // Валидация перед отправкой
            document.querySelector('form[method="POST"]').addEventListener('submit', function(e) {
                const key = document.getElementById('keyInput').value;
                const pattern = /^ELIZA-\d{8}-[A-Z0-9]{4}-[A-Z0-9]{4}$/;
                if (!pattern.test(key)) {
                    e.preventDefault();
                    alert('Неверный формат ключа! Используйте формат: ELIZA-YYYYMMDD-XXXX-XXXX');
                }
            });
        </script>
    </body>
    </html>
    """


# Создаём админ-панель
admin_app = FastAPI(title="Eliza Admin", docs_url=None, redoc_url=None)


@admin_app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    if get_current_admin(request, db):
        return RedirectResponse(url="/admin/dashboard")
    return get_login_html()


@admin_app.post("/authenticate")
async def authenticate(request: Request, password: str = Form(...), db: Session = Depends(get_db)):
    admin = db.query(AdminUser).first()

    if not admin or not verify_password(password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный пароль")

    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")

    token = create_access_token(data={"sub": admin.username})

    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(key="admin_token", value=token, httponly=True, max_age=604800)
    return response


@admin_app.get("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_token")
    return response


@admin_app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login")
    return get_dashboard_html(admin, db)


# ===== API для управления лицензиями =====

@admin_app.get("/licensekey/")
async def list_keys(request: Request, db: Session = Depends(get_db)):
    """Список лицензий"""
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login")
    
    keys = db.query(LicenseKey).order_by(LicenseKey.created_at.desc()).all()
    return {"keys": [{"id": k.id, "key": k.key, "is_activated": k.is_activated, 
                      "activation_count": k.activation_count, 
                      "max_activations": k.max_activations} for k in keys]}


@admin_app.post("/licensekey/create")
async def create_key(request: Request, db: Session = Depends(get_db)):
    """Создание ключа"""
    admin = get_current_admin(request, db)
    if not admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    form = await request.form()
    key = form.get("key", "")
    max_activations = int(form.get("max_activations", 1))
    
    new_key = LicenseKey(key=key.upper(), max_activations=max_activations)
    db.add(new_key)
    db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@admin_app.delete("/licensekey/{key_id}")
async def delete_key(request: Request, key_id: int, db: Session = Depends(get_db)):
    """Удаление ключа"""
    admin = get_current_admin(request, db)
    if not admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    key = db.query(LicenseKey).filter(LicenseKey.id == key_id).first()
    if key:
        db.delete(key)
        db.commit()
    return {"success": True}
