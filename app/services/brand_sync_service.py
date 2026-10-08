from sqlalchemy.orm import Session

from app.models.brand import Brand
from app.services.brands_service import fetch_external_brands


async def sync_brands(db: Session):

    response = await fetch_external_brands()

    external_brands = response.get("data", [])

    synced = 0
    created = 0
    updated = 0

    for external_brand in external_brands:

        external_id = external_brand.get("slug")
        name = external_brand.get("name")
        logo_url = external_brand.get("logo")

        if not external_id or not name:
            continue

        existing_brand = (
            db.query(Brand)
            .filter(Brand.external_id == external_id)
            .first()
        )

        if existing_brand:

            existing_brand.name = name
            existing_brand.logo_url = logo_url
            existing_brand.is_active = True

            updated += 1

        else:

            new_brand = Brand(
                external_id=external_id,
                name=name,
                logo_url=logo_url,
                is_active=True,
            )

            db.add(new_brand)

            created += 1

        synced += 1

    db.commit()

    return {
        "synced": synced,
        "created": created,
        "updated": updated,
    }