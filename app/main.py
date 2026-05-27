from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "env": settings.env,
    }
@app.get("/api/info")
def get_app_info() -> dict[str, str]:
    return {
        "app_name": settings.app_name,
        "env": settings.env,
        "api_prefix": settings.api_prefix,
    }
