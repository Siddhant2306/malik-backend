import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.brand import Brand
from app.models.converter import Converter
from app.services.brands_service import fetch_external_brands
from app.services.brand_sync_service import sync_brands
from app.core.rate_limit import rate_limiter
from app.core.permission import get_current_admin, get_current_approved_user
from app.models.users import Users


router = APIRouter(
    prefix="/api/v1/brands",
    tags=["Brands"],
)
logger = logging.getLogger(__name__)

@router.get("")
def get_brands(
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_approved_user)
):
    rows = (
        db.query(
            Brand.id,
            Brand.external_id,
            Brand.name,
            Brand.logo_url,
            func.count(Converter.id).label("converter_count"),
        )
        .outerjoin(
            Converter,
            (Converter.brand_id == Brand.id)
            & (Converter.is_active.is_(True)),
        )
        .filter(Brand.is_active.is_(True))
        .group_by(
            Brand.id,
            Brand.external_id,
            Brand.name,
            Brand.logo_url,
        )
        .order_by(Brand.name.asc())
        .all()
    )

    return [
        {
            "id": row.id,
            "external_id": row.external_id,
            "name": row.name,
            "logo_url": row.logo_url,
            "converter_count": row.converter_count,
        }
        for row in rows
    ]

@router.get("/external")
async def get_external_brands(
    user: Users = Depends(get_current_approved_user),
):

    try:
        response = await fetch_external_brands()

        return response

    except Exception:
        logger.exception("External brand provider request failed.")
        raise HTTPException(
            status_code=502,
            detail="The external brand provider is unavailable.",
        )


@router.post("/sync")
async def sync_external_brands(
    db: Session = Depends(get_db),
    admin: Users = Depends(get_current_admin),
):
    rate_limiter.check(
        key=f"brand-sync:{admin.id}",
        limit=3,
        window_seconds=3600,
    )
    try:
        result = await sync_brands(db)
        return result
    except Exception:
        logger.exception("Brand sync failed for admin %s.", admin.id)

        raise HTTPException(
            status_code=502,
            detail="The brand sync could not be completed.",
        )
