from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.core.permission import get_current_admin
from app.models.users import Users
from app.services.image_service import upload_converter_image


router = APIRouter(
    prefix="/api/v1/uploads",
    tags=["Uploads"],
)

_MAX_IMAGE_BYTES = 5 * 1024 * 1024
_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _has_supported_signature(content: bytes) -> bool:
    return (
        content.startswith(b"\xff\xd8\xff")
        or content.startswith(b"\x89PNG\r\n\x1a\n")
        or (content.startswith(b"RIFF") and content[8:12] == b"WEBP")
    )


@router.post("/converter-image")
async def upload_converter_image_endpoint(
    file: UploadFile = File(...),
    admin: Users = Depends(get_current_admin),
):
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, and WebP images are supported.",
        )

    content = await file.read(_MAX_IMAGE_BYTES + 1)
    await file.close()
    if not content or len(content) > _MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image files must be 5 MB or smaller.",
        )
    if not _has_supported_signature(content):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="The uploaded file does not contain a supported image.",
        )

    # Cloudinary's SDK is synchronous. Keep its network round trip off the
    # event loop so other API requests remain responsive while an image uploads.
    result = await run_in_threadpool(upload_converter_image, BytesIO(content))

    return result
