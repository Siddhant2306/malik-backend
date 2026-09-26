from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Converter(Base):
    __tablename__ = "converters"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    brand_id: Mapped[int] = mapped_column(
        ForeignKey("brands.id"),
        nullable=False,
        index=True
    )

    code_reference: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )

    model: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True
    )

    country: Mapped[str] = mapped_column(
        String(100),
        default="India",
        server_default="India",
        nullable=False
    )

    converter_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    local_lingo: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        index=True
    )

    monolith_weight_g: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    pt_ppm: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4),
        nullable=True
    )

    pd_ppm: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4),
        nullable=True
    )

    rh_ppm: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4),
        nullable=True
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    brand = relationship(
        "Brand",
        back_populates="converters"
    )

    markings = relationship(
        "ConverterMarking",
        back_populates="converter",
        cascade="all, delete-orphan"
    )

    images = relationship(
        "ConverterImage",
        back_populates="converter",
        cascade="all, delete-orphan"
    )