# Точка входа для приложения
# Этот файл импортирует app из app.main для совместимости с различными платформами деплоя

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
