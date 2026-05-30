from fastapi import FastAPI
from src.config import get_settings
from src.core.errors.handlers import register_exception_handlers
from src.core.logger import RequestLoggingMiddleware, setup_logging
from src.users.router import router as users_router
from src.courses.router import router as courses_router
from src.sections.router import router as sections_router


settings=get_settings()

def create_app()-> FastAPI:
    app = FastAPI(
        title="LMS Backend",
        version="0.1.0",
        debug=settings.app_debug,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,

    )

    app.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(app)
    
    app.include_router(users_router, prefix="/users", tags=["users"])
    app.include_router(courses_router, prefix="/courses", tags=["courses"])
    app.include_router(sections_router, prefix="/courses", tags=["sections"])

    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()