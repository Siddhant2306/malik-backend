from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ConverterImage(Base):
    __tablename__ = "converter_images"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    converter_id: Mapped[int] = mapped_column(
        ForeignKey("converters.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    display_order: Mapped[int] = mapped_column(
        default=0,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    converter = relationship(
        "Converter",
        back_populates="images"
    )