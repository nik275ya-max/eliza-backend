# 🚀 Деплой на Timeweb Cloud App Platform (SQLite)

## 📋 Шаг 1: Создайте приложение в Timeweb

1. Зайдите в панель Timeweb Cloud: https://timeweb.cloud
2. Перейдите в **App Platform** → **Создать приложение**
3. Выберите **Подключить репозиторий GitHub**
4. Авторизуйтесь на GitHub
5. Выберите репозиторий: `nik275ya-max/eliza-backend`
6. Ветка: **main**

---

## 📋 Шаг 2: Настройте сборку

**Dockerfile:** `Dockerfile.timeweb`

**Переменные окружения:**

| Ключ | Значение |
|------|----------|
| `SECRET_KEY` | `your-super-secret-key-min-32-chars` |
| `ADMIN_USERNAME` | `admin` |
| `ADMIN_PASSWORD` | `CHANGE_THIS_PASSWORD_123` |
| `ADMIN_EMAIL` | `admin@eliza.local` |
| `DEBUG` | `false` |
| `CORS_ORIGINS` | `["*"]` |

**База данных:** SQLite (файл `eliza.db` создаётся автоматически)

---

## 📋 Шаг 3: Настройки приложения

- **Имя**: `eliza-backend`
- **Регион**: Выберите ближайший (например, `Москва`)
- **План**: Начните с минимального (128 MB)
- **Порт**: `8000`

---

## 📋 Шаг 4: Запуск

1. Нажмите **Создать приложение**
2. Дождитесь сборки (2-5 минут)
3. Приложение получит URL вида: `https://eliza-backend-xxx.tw1.ru`

---

## 📋 Шаг 5: Проверка

### 5.1 Проверка работоспособности

```
https://eliza-backend-xxx.tw1.ru/health
```

Должны увидеть:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-27T12:00:00Z"
}
```

### 5.2 Админ-панель

```
https://eliza-backend-xxx.tw1.ru/admin
```

**Логин:** `admin`  
**Пароль:** тот, что указали в `ADMIN_PASSWORD`

### 5.3 Тест API

```bash
curl -X POST https://eliza-backend-xxx.tw1.ru/api/v1/license/activate \
  -H "Content-Type: application/json" \
  -d '{"key": "ELIZA-20261231-A1B2-C3D4"}'
```

---

## 📋 Шаг 6: Создание лицензий

### Через админ-панель:

1. Откройте `/admin`
2. Раздел **Лицензионные ключи**
3. Нажмите **Создать**
4. Введите ключ: `ELIZA-20261231-A1B2-C3D4`
5. Max activations: `1`

### Через API:

```bash
# Логин в админку
curl -X POST https://eliza-backend-xxx.tw1.ru/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=CHANGE_THIS_PASSWORD_123"

# Создание ключа (используйте токен из ответа)
curl -X POST https://eliza-backend-xxx.tw1.ru/api/v1/license/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"key": "ELIZA-20261231-A1B2-C3D4", "max_activations": 1}'
```

---

## 📝 Важное примечание о SQLite

⚠️ **SQLite хранит данные в файле** `eliza.db`. При перезапуске приложения данные **сохраняются**.

Однако, если вы хотите **надёжное хранение** для продакшена — рассмотрите:
- **PostgreSQL** (добавить в Timeweb)
- **Резервное копирование** файла `eliza.db`

---

## 💰 Стоимость

| Тариф | RAM | CPU | Цена/мес |
|-------|-----|-----|----------|
| Start | 128 MB | 0.2 ядра | ~150 ₽ |

**SQLite:** бесплатно (входит в тариф)

---

## 🔧 Обновление приложения

```bash
cd C:\Users\Nik\eliza-backend
git add .
git commit -m "Update: описание"
git push origin main
```

Timeweb автоматически пересоберёт (1-2 минуты).

---

**Готово!** 🎉
