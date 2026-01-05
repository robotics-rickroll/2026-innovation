from __future__ import annotations
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.enums import ClassificationStatus, ProviderName


class ClassificationBase(BaseModel):
    status: ClassificationStatus
    summary: Optional[str] = None
    artifact_type: Optional[str] = None
    civilization: Optional[str] = None
    age_range: Optional[str] = None
    confidence: Optional[float] = None


class ClassificationCreate(ClassificationBase):
    raw_response: Optional[dict[str, Any]] = None
    provider: Optional[ProviderName] = None


class ClassificationUpdate(BaseModel):
    status: Optional[ClassificationStatus] = None
    summary: Optional[str] = None
    artifact_type: Optional[str] = None
    civilization: Optional[str] = None
    age_range: Optional[str] = None
    confidence: Optional[float] = None


class ClassificationResult(ClassificationBase):
    id: str
    raw_response: Optional[dict[str, Any]] = None
    provider: ProviderName
    created_at: datetime

    class Config:
        from_attributes = True
