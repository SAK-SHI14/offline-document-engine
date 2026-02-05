from fastapi import FastAPI
from .core.config import settings
from .core.logging import logger
from .api.v1.endpoints import router as api_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    logger.info("Initializing Document Engine...")

    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/health")
    def health_check():
        return {"status": "ok", "app": settings.APP_NAME}

    @app.get("/")
    def root():
        return {"message": "Document Engine is running. Visit /docs for API documentation."}

    return app

app = create_app()
