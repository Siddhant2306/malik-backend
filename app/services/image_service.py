import cloudinary.uploader


def upload_converter_image(file):
    result = cloudinary.uploader.upload(
        file,
        folder="malik/converters",
        resource_type="image",
    )

    return {
        "public_id": result["public_id"],
        "image_url": result["secure_url"],
        "width": result.get("width"),
        "height": result.get("height"),
        "format": result.get("format"),
    }