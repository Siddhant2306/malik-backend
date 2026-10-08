from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.convertor.route import router as converter_router
from app.api.metals.route import router as metals
from app.api.brands.route import router as brands_router
from app.api.auth.route import router as auth_router
from app.api.admin.route import router as admin_users_router
from app.api.upload.route import router as uploads_router


app = FastAPI(
    title="MALIK Backend",
    description="Backend API for MALIK – Catalytic Converter Catalog",
    version="1.0.0",
)


app.include_router(converter_router)
app.include_router(metals)
app.include_router(brands_router)
app.include_router(auth_router)
app.include_router(admin_users_router)
app.include_router(uploads_router)

print("METALS ROUTER:")
for route in metals.routes:
    print(
        type(route),
        getattr(route, "path", None),
        getattr(route, "methods", None)
    )


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