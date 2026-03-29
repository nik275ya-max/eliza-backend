# Точка входа для приложения
# Минимальная версия для проверки работоспособности

try:
    from app.main import app
except Exception as e:
    print(f"ERROR importing app: {e}")
    # Fallback - минимальное приложение
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return {"message": "Eliza Backend - Error loading main app"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
