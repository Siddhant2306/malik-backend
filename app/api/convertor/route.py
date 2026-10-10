from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.permission import get_current_admin
from app.db.session import get_db
from app.models.users import Users
from app.schemas.converter import ConverterCreate
from app.services.converter_service import create_converter


router = APIRouter(
    prefix="/api/v1/admin/converters",
    tags=["Admin - Converters"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def add_converter(
    data: ConverterCreate,
    db: Session = Depends(get_db),
    admin: Users = Depends(get_current_admin)
):
    converter = create_converter(db, data)

    return {
        "message": "Converter created successfully",
        "converter_id": converter.id,
    }