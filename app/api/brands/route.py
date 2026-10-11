from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.brand import Brand
from app.models.converter import Converter
from app.services.brands_service import fetch_external_brands
from app.services.brand_sync_service import sync_brands


router = APIRouter(
    prefix="/api/v1/brands",
    tags=["Brands"],
)

@router.get("")
def get_brands(
    db: Session = Depends(get_db),
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
async def get_external_brands():

    try:
        response = await fetch_external_brands()

        return response

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch external brands: {str(e)}",
        )


@router.post("/sync")
async def sync_external_brands(
    db: Session = Depends(get_db),
):

    try:

        result = await sync_brands(db)

        return result

    except Exception as e:

        raise HTTPException(
            status_code=502,
            detail=f"Failed to sync brands: {str(e)}",
        )