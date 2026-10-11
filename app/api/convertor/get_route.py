
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.brand import Brand
from app.models.converter import Converter
from app.models.converter_marking import ConverterMarking
from app.models.converter_image import ConverterImage

from app.core.permission import get_current_admin, get_current_approved_user
from app.models.users import Users

router = APIRouter(
    prefix="/api/v1/converters",
    tags=["Converters"],
)


def converter_to_dict(
    db: Session,
    converter: Converter,
    include_details: bool = False,
) -> dict:
    brand = (
        db.query(Brand)
        .filter(Brand.id == converter.brand_id)
        .first()
    )

    images = (
        db.query(ConverterImage)
        .filter(ConverterImage.converter_id == converter.id)
        .order_by(ConverterImage.display_order.asc())
        .all()
    )

    markings = (
        db.query(ConverterMarking)
        .filter(ConverterMarking.converter_id == converter.id)
        .all()
    )

    result = {
        "id": converter.id,
        "brand_id": converter.brand_id,
        "brand_name": brand.name if brand else None,
        "code_reference": converter.code_reference,
        "model": converter.model,
        "monolith_weight_g": converter.monolith_weight_g,
        "converter_type": converter.converter_type,
        "category": converter.category,
        "markings": [m.marking for m in markings],
        "images": [
            {
                "id": image.id,
                "image_url": image.image_url,
                "display_order": image.display_order,
            }
            for image in images
        ],
    }

    if include_details:
        result.update({
            "country": converter.country,
            "local_lingo": converter.local_lingo,
            "pt_ppm": converter.pt_ppm,
            "pd_ppm": converter.pd_ppm,
            "rh_ppm": converter.rh_ppm,
            "remarks": converter.remarks,
            "notes": converter.notes,
        })

    return result


@router.get("")
def get_converters(
    search: str | None = Query(default=None, min_length=1),
    brand_id: int | None = Query(default=None, gt=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Users = Depends(get_current_admin)
):
    query = (
        db.query(Converter)
        .filter(Converter.is_active.is_(True))
    )

    if brand_id is not None:
        query = query.filter(Converter.brand_id == brand_id)

    if search:
        term = f"%{search.strip()}%"
        query = (
            query.join(
                Brand,
                Brand.id == Converter.brand_id,
            )
            .filter(
                or_(
                    Converter.code_reference.ilike(term),
                    Converter.model.ilike(term),
                    Brand.name.ilike(term),
                    Converter.local_lingo.ilike(term),
                    Converter.remarks.ilike(term),
                )
            )
        )

    total = query.count()

    converters = (
        query
        .order_by(Converter.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            converter_to_dict(db, converter)
            for converter in converters
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{converter_id}")
def get_converter_detail(
    converter_id: int,
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_approved_user)
):
    converter = (
        db.query(Converter)
        .filter(
            Converter.id == converter_id,
            Converter.is_active.is_(True),
        )
        .first()
    )

    if converter is None:
        raise HTTPException(
            status_code=404,
            detail="Converter not found",
        )

    return converter_to_dict(
        db,
        converter,
        include_details=True,
    )
