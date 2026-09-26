from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.routes import router as converter_router


app = FastAPI(
    title="MALIK Backend",
    description="Backend API for MALIK – Catalytic Converter Catalog",
    version="1.0.0",
)


app.include_router(converter_router)


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