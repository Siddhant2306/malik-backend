from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


_MAX_IMAGES = 4
_MAX_MARKINGS = 25


class _ConverterPayload(BaseModel):
    model: str | None = Field(default=None, max_length=150)
    country: str = Field(default="India", min_length=1, max_length=100)
    converter_type: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=100)
    local_lingo: str | None = Field(default=None, max_length=200)

    monolith_weight_g: Decimal | None = Field(default=None, ge=0)
    pt_ppm: Decimal | None = Field(default=None, ge=0)
    pd_ppm: Decimal | None = Field(default=None, ge=0)
    rh_ppm: Decimal | None = Field(default=None, ge=0)

    markings: list[str] = Field(default_factory=list, max_length=_MAX_MARKINGS)
    images: list[str] = Field(default_factory=list, max_length=_MAX_IMAGES)
    remarks: str | None = Field(default=None, max_length=5000)
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator(
        "model",
        "converter_type",
        "category",
        "local_lingo",
        "remarks",
        "notes",
    )
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Country cannot be blank.")
        return normalized

    @field_validator("markings")
    @classmethod
    def validate_markings(cls, values: list[str]) -> list[str]:
        normalized = []
        for value in values:
            marking = value.strip()
            if not marking or len(marking) > 200:
                raise ValueError("Each marking must contain 1 to 200 characters.")
            normalized.append(marking)
        return normalized

    @field_validator("images")
    @classmethod
    def validate_images(cls, values: list[str]) -> list[str]:
        normalized = []
        for value in values:
            image_url = value.strip()
            if not image_url.startswith("https://") or len(image_url) > 500:
                raise ValueError("Each image must be an HTTPS URL up to 500 characters.")
            normalized.append(image_url)
        return normalized


class ConverterCreate(_ConverterPayload):
    brand_id: int = Field(gt=0)
    code_reference: str = Field(min_length=1, max_length=150)

    @field_validator("code_reference")
    @classmethod
    def normalize_reference(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Code reference cannot be blank.")
        return normalized


class ConverterUpdate(_ConverterPayload):
    brand_id: int | None = Field(default=None, gt=0)
    code_reference: str | None = Field(default=None, min_length=1, max_length=150)

    @field_validator("brand_id", "code_reference", mode="before")
    @classmethod
    def reject_null_for_required_fields(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value

    @field_validator("code_reference")
    @classmethod
    def normalize_optional_reference(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Code reference cannot be blank.")
        return normalized


class ConverterBulkCreate(BaseModel):
    converters: list[ConverterCreate] = Field(min_length=1, max_length=100)


class ConverterResponse(BaseModel):
    id: int
    converter_code: str
    brand_id: int
    code_reference: str
    model: str | None
    country: str
    converter_type: str | None
    category: str | None
    local_lingo: str | None
    monolith_weight_g: Decimal | None
    pt_ppm: Decimal | None
    pd_ppm: Decimal | None
    rh_ppm: Decimal | None
    remarks: str | None
    notes: str | None
    markings: list[str]
    images: list[str]
    created_at: datetime

    class Config:
        from_attributes = True
