from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permission import get_current_admin
from app.db.session import get_db
from app.models.converter import Converter
from app.models.users import Users
from app.schemas.converter import ConverterBulkCreate, ConverterCreate, ConverterUpdate
from app.services.converter_service import (
    create_converter,
    create_converters_bulk,
    delete_converter,
    update_converter,
)


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
    admin: Users = Depends(get_current_admin),
):
    try:
        converter = create_converter(db, data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return {
        "message": "Converter created successfully",
        "converter_id": converter.id,
        "converter_code": converter.converter_code,
    }


@router.post(
    "/bulk",
    status_code=status.HTTP_201_CREATED,
)
def add_converters_bulk(
    data: ConverterBulkCreate,
    db: Session = Depends(get_db),
    admin: Users = Depends(get_current_admin),
):
    try:
        converters = create_converters_bulk(db, data.converters)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    return {
        "message": "Converters imported successfully",
        "converter_ids": [converter.id for converter in converters],
        "count": len(converters),
    }


def get_active_converter(db: Session, converter_id: int) -> Converter:
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Converter not found",
        )
    return converter


@router.patch("/{converter_id}")
def edit_converter(
    converter_id: int,
    data: ConverterUpdate,
    db: Session = Depends(get_db),
    admin: Users = Depends(get_current_admin),
):
    converter = get_active_converter(db, converter_id)
    try:
        converter = update_converter(db, converter, data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return {
        "message": "Converter updated successfully",
        "converter_id": converter.id,
        "converter_code": converter.converter_code,
    }


@router.delete("/{converter_id}")
def remove_converter(
    converter_id: int,
    db: Session = Depends(get_db),
    admin: Users = Depends(get_current_admin),
):
    converter = get_active_converter(db, converter_id)
    delete_converter(db, converter)
    return {
        "message": "Converter deleted successfully",
        "converter_id": converter.id,
    }
