from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
#from unittest.mock import Base


from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class ConverterMarking(Base):
    __tablename__ = "converter_markings"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    converter_id: Mapped[int] = mapped_column(
        ForeignKey("converters.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    marking: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    converter = relationship(
        "Converter",
        back_populates="markings"
    )
