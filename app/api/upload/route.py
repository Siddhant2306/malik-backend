from fastapi import APIRouter, Depends, File, UploadFile

from app.core.permission import get_current_admin
from app.models.users import Users
from app.services.image_service import upload_converter_image


router = APIRouter(
    prefix="/api/v1/uploads",
    tags=["Uploads"],
)


@router.post("/converter-image")
async def upload_converter_image_endpoint(
    file: UploadFile = File(...),
    admin: Users = Depends(get_current_admin),
):
    result = upload_converter_image(file.file)

    return result