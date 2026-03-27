# Eliza License Backend

Бэкенд для управления лицензиями на FastAPI + SQLite с админ-панелью.

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка

```bash
# Копирование .env
copy .env.example .env
```

Откройте `.env` и настройте:

```env
DATABASE_URL=sqlite:///./eliza.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
SECRET_KEY=your-secret-key-change-in-production
```

### 3. Запуск

```bash
# Разработка
uvicorn app.main:app --reload

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📡 API

### Публичные эндпоинты

#### POST /api/v1/license/activate

Активация лицензионного ключа.

**Запрос:**
```json
{
  "key": "ELIZA-20261231-A1B2-C3D4"
}
```

**Ответ:**
```json
{
  "valid": true,
  "activated": true,
  "activation_count": 1,
  "max_activations": 1,
  "expires_formatted": "31.12.2026"
}
```

#### GET /api/v1/license/stats

Статистика по лицензиям (требуется авторизация).

#### GET /health

Проверка работоспособности.

### Админ-панель

Откройте `/admin` для доступа к админ-панели.

**Логин по умолчанию:**
- Username: `admin`
- Password: `admin123`

**Возможности:**
- Просмотр всех лицензионных ключей
- Создание новых ключей
- Редактирование ключей
- Удаление ключей
- Управление администраторами

## 🗄️ База данных

### Таблица `license_keys`

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | ID записи |
| key | VARCHAR(26) | Лицензионный ключ |
| is_activated | BOOLEAN | Флаг активации |
| activation_count | INTEGER | Текущее число активаций |
| max_activations | INTEGER | Максимум активаций |
| created_at | DATETIME | Дата создания |

### Таблица `admin_users`

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | ID записи |
| username | VARCHAR(50) | Имя пользователя |
| email | VARCHAR(100) | Email |
| hashed_password | VARCHAR(255) | Хешированный пароль |
| is_active | BOOLEAN | Активен ли |
| created_at | DATETIME | Дата создания |

## 🔐 Авторизация

### POST /api/v1/auth/login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 📁 Структура проекта

```
eliza-backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # Точка входа
│   ├── admin/            # Админ-панель
│   ├── api/              # API роуты
│   │   ├── licenses.py   # Лицензии
│   │   └── admin.py      # Авторизация
│   ├── core/             # Ядро
│   │   ├── config.py     # Конфигурация
│   │   ├── database.py   # БД
│   │   └── security.py   # Безопасность
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   └── services/         # Бизнес-логика
├── templates/            # Шаблоны для админки
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Деплой на TimeWeb

### 1. Подготовка

```bash
# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка на сервере

1. Загрузите файлы на сервер через FTP/SFTP
2. Создайте `.env` файл с настройками
3. Настройте базу данных (SQLite или PostgreSQL)

### 3. Запуск через gunicorn

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4. Настройка nginx (опционально)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🧪 Тестирование

### Через Swagger UI

Откройте http://localhost:8000/docs

### Через curl

```bash
# Активация ключа
curl -X POST http://localhost:8000/api/v1/license/activate \
  -H "Content-Type: application/json" \
  -d '{"key": "ELIZA-20261231-A1B2-C3D4"}'

# Проверка здоровья
curl http://localhost:8000/health
```

## 🔒 Безопасность

- ✅ Валидация формата ключа (ELIZA-YYYYMMDD-XXXX-XXXX)
- ✅ Проверка даты истечения
- ✅ Ограничение количества активаций
- ✅ JWT авторизация для админки
- ✅ Хеширование паролей (bcrypt)
- ✅ CORS настройка

## 📝 Лицензия

MIT
