from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ConverterCreate(BaseModel):
    brand_id: int
    code_reference: str = Field(min_length=1, max_length=150)

    model: str | None = None

    converter_type: str | None = None
    category: str | None = None
    local_lingo: str | None = None

    monolith_weight_g: Decimal | None = None

    pt_ppm: Decimal | None = None
    pd_ppm: Decimal | None = None
    rh_ppm: Decimal | None = None

    markings: list[str] = []

    images: list[str] = []

    remarks: str | None = None
    notes: str | None = None

class ConverterResponse(BaseModel):
    id: int
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