from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.api.convertor.route import router as converter_router
from app.api.metals.route import router as metals
from app.api.brands.route import router as brands_router
from app.api.auth.route import router as auth_router
from app.api.admin.route import router as admin_users_router
from app.api.upload.route import router as uploads_router
from app.api.convertor.get_route import router as get_converter_router


app = FastAPI(
    title=settings.app_name,
    description="Backend API for MALIK – Catalytic Converter Catalog",
    version="1.0.0",
    debug=settings.debug,
)

_cors_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]
if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=()")
    return response


app.include_router(converter_router)
app.include_router(metals)
app.include_router(brands_router)
app.include_router(auth_router)
app.include_router(admin_users_router)
app.include_router(uploads_router)
app.include_router(get_converter_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "malik-backend"
    }


@app.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected"
    }
