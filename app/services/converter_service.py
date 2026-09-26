from sqlalchemy.orm import Session

from app.models.converter import Converter
from app.models.converter_marking import ConverterMarking
from app.models.converter_image import ConverterImage
from app.schemas.converter import ConverterCreate


def create_converter(
    db: Session,
    data: ConverterCreate
) -> Converter:

    converter = Converter(
        brand_id=data.brand_id,
        code_reference=data.code_reference,
        model=data.model,
        country="India",
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