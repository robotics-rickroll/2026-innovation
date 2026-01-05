from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ClassificationStatus, ProviderName


class ClassificationResult(Base):
    __tablename__ = "classification_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    artifact_id: Mapped[str] = mapped_column(String(36), ForeignKey("artifacts.id"), index=True)
    status: Mapped[ClassificationStatus] = mapped_column(Enum(ClassificationStatus), default=ClassificationStatus.PENDING)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    artifact_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    civilization: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    age_range: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    raw_response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    provider: Mapped[ProviderName] = mapped_column(Enum(ProviderName), default=ProviderName.mock)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    artifact: Mapped["Artifact"] = relationship("Artifact", back_populates="classifications")
