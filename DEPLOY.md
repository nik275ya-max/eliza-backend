# 🚀 Инструкция по отправке на GitHub

## Вариант 1: Через Git Bash

Откройте Git Bash в папке проекта и выполните:

```bash
cd C:/Users/Nik/eliza-backend

# Добавьте удалённый репозиторий
git remote add origin https://github.com/nik275ya-max/eliza-backend.git

# Запушьте код
git push -u origin main
```

---

## Вариант 2: Через GitHub Desktop

1. Откройте GitHub Desktop
2. File → Add Local Repository → Выберите `C:\Users\Nik\eliza-backend`
3. File → Repository Settings → Remote → Вставьте URL:
   ```
   https://github.com/nik275ya-max/eliza-backend.git
   ```
4. Нажмите Push

---

## Вариант 3: Через VS Code

1. Откройте папку в VS Code
2. Перейдите во вкладку Source Control
3. Нажмите Publish to GitHub
4. Выберите репозиторий `nik275ya-max/eliza-backend`

---

## Проверка

Откройте https://github.com/nik275ya-max/eliza-backend и убедитесь, что файлы загружены.

---

## 📝 Быстрый старт локально

```bash
cd C:\Users\Nik\eliza-backend

# Установка зависимостей
pip install -r requirements.txt

# Копирование .env
copy .env.example .env

# Запуск
uvicorn app.main:app --reload
```

Откройте http://localhost:8000/admin для админ-панели.

**Логин по умолчанию:**
- Username: `admin`
- Password: `admin123`
