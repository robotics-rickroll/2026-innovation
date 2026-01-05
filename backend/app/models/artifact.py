from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    artifact_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    location_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_approx: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    measure_length_cm: Mapped[float] = mapped_column(Float)
    measure_width_cm: Mapped[float] = mapped_column(Float)
    measure_height_cm: Mapped[float] = mapped_column(Float)
    additional_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    images: Mapped[list["ArtifactImage"]] = relationship(
        "ArtifactImage", back_populates="artifact", cascade="all, delete-orphan"
    )
    classifications: Mapped[list["ClassificationResult"]] = relationship(
        "ClassificationResult", back_populates="artifact", cascade="all, delete-orphan"
    )
