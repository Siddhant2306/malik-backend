from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.brand import Brand
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
    brands = (
        db.query(Brand)
        .filter(Brand.is_active == True)
        .order_by(Brand.name.asc())
        .all()
    )

    return [
        {
            "id": brand.id,
            "external_id": brand.external_id,
            "name": brand.name,
            "logo_url": brand.logo_url,
        }
        for brand in brands
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