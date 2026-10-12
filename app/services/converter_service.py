from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.brand import Brand
from app.models.converter import Converter
from app.models.converter_marking import ConverterMarking
from app.models.converter_image import ConverterImage
from app.schemas.converter import ConverterCreate, ConverterUpdate
from app.services.converter_code import generate_converter_prefix


def create_converter(
    db: Session,
    data: ConverterCreate
) -> Converter:
    brand = db.query(Brand).filter(Brand.id == data.brand_id).first()
    if brand is None:
        raise ValueError("Brand not found")

    converter = Converter(
        converter_code=f"TEMP-{uuid4().hex}",
        brand_id=data.brand_id,
        code_reference=data.code_reference,
        model=data.model,
        country=data.country,
        converter_type=data.converter_type,
        category=data.category,
        local_lingo=data.local_lingo,
        monolith_weight_g=data.monolith_weight_g,
        pt_ppm=data.pt_ppm,
        pd_ppm=data.pd_ppm,
        rh_ppm=data.rh_ppm,
        remarks=data.remarks,
        notes=data.notes,
    )

    db.add(converter)
    db.flush()
    prefix = generate_converter_prefix(converter.country, brand.name)
    converter.converter_code = f"{prefix}-{converter.id:06d}"

    for marking in data.markings:
        converter_marking = ConverterMarking(
            converter_id=converter.id,
            marking=marking,
        )

        db.add(converter_marking)

    for index, image_url in enumerate(data.images):
        converter_image = ConverterImage(
            converter_id=converter.id,
            image_url=image_url,
            display_order=index,
        )

        db.add(converter_image)

    db.commit()
    db.refresh(converter)

    return converter


def update_converter(
    db: Session,
    converter: Converter,
    data: ConverterUpdate,
) -> Converter:
    changes = data.model_dump(exclude_unset=True)
    markings = changes.pop("markings", None)
    images = changes.pop("images", None)

    if "brand_id" in changes:
        brand = db.query(Brand).filter(Brand.id == changes["brand_id"]).first()
        if brand is None:
            raise ValueError("Brand not found")

    for field, value in changes.items():
        setattr(converter, field, value)

    if markings is not None:
        db.query(ConverterMarking).filter(
            ConverterMarking.converter_id == converter.id
        ).delete(synchronize_session=False)
        for marking in markings:
            db.add(ConverterMarking(
                converter_id=converter.id,
                marking=marking,
            ))

    if images is not None:
        db.query(ConverterImage).filter(
            ConverterImage.converter_id == converter.id
        ).delete(synchronize_session=False)
        for index, image_url in enumerate(images):
            db.add(ConverterImage(
                converter_id=converter.id,
                image_url=image_url,
                display_order=index,
            ))

    db.commit()
    db.refresh(converter)
    return converter


def delete_converter(db: Session, converter: Converter) -> None:
    converter.is_active = False
    db.commit()