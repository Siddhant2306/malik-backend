
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.brand import Brand
from app.models.converter import Converter

from app.core.permission import get_current_approved_user
from app.models.users import Users

router = APIRouter(
    prefix="/api/v1/converters",
    tags=["Converters"],
)


def converter_to_dict(
    converter: Converter,
    include_details: bool = False,
) -> dict:
    result = {
        "id": converter.id,
        "converter_code": converter.converter_code,
        "brand_id": converter.brand_id,
        "brand_name": converter.brand.name if converter.brand else None,
        "code_reference": converter.code_reference,
        "model": converter.model,
        "monolith_weight_g": converter.monolith_weight_g,
        "converter_type": converter.converter_type,
        "category": converter.category,
        "markings": [marking.marking for marking in converter.markings],
        "images": [
            {
                "id": image.id,
                "image_url": image.image_url,
                "display_order": image.display_order,
            }
            for image in sorted(
                converter.images,
                key=lambda converter_image: converter_image.display_order,
            )
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
    search: str | None = Query(default=None, max_length=100),
    brand_id: int | None = Query(default=None, gt=0),
    cursor: int | None = Query(default=None, gt=0),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_approved_user)
):
    if search is not None:
        search = search.strip()
        if search and len(search) < 3:
            raise HTTPException(
                status_code=422,
                detail="Search term must contain at least 3 non-whitespace characters.",
            )
        if not search:
            search = None

    query = (
        db.query(Converter)
        .filter(Converter.is_active.is_(True))
    )

    if cursor is not None:
        query = query.filter(Converter.id < cursor)

    if brand_id is not None:
        query = query.filter(Converter.brand_id == brand_id)

    if search:
        escaped_search = (
            search
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        term = f"%{escaped_search}%"
        query = (
            query.join(
                Brand,
                Brand.id == Converter.brand_id,
            )
            .filter(
                or_(
                    Converter.code_reference.ilike(term, escape="\\"),
                    Converter.model.ilike(term, escape="\\"),
                    Brand.name.ilike(term, escape="\\"),
                    Converter.local_lingo.ilike(term, escape="\\"),
                    Converter.remarks.ilike(term, escape="\\"),
                )
            )
        )

    converters = (
        query
        .options(
            selectinload(Converter.brand),
            selectinload(Converter.images),
            selectinload(Converter.markings),
        )
        .order_by(Converter.id.desc())
        .limit(page_size + 1)
        .all()
    )

    has_more = len(converters) > page_size
    converters = converters[:page_size]

    return {
        "items": [
            converter_to_dict(converter)
            for converter in converters
        ],
        "next_cursor": converters[-1].id if has_more else None,
        "has_more": has_more,
        "page_size": page_size,
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
        converter,
        include_details=True,
    )
