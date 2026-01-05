from __future__ import annotations
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ArtifactBase(BaseModel):
    artifact_id: str
    timestamp: Optional[datetime] = None
    location_approx: Optional[str] = None
    measure_length_cm: float
    measure_width_cm: float
    measure_height_cm: float
    additional_info: Optional[dict[str, Any]] = None


class ArtifactCreate(BaseModel):
    artifact_id: str = Field(..., examples=["ART-000123"])
    timestamp: Optional[datetime] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    measure_length_cm: float
    measure_width_cm: float
    measure_height_cm: float
    additional_info: Optional[dict[str, Any]] = None
    image_urls: list[str] = []


class ArtifactUpdate(BaseModel):
    timestamp: Optional[datetime] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    measure_length_cm: Optional[float] = None
    measure_width_cm: Optional[float] = None
    measure_height_cm: Optional[float] = None
    additional_info: Optional[dict[str, Any]] = None


class ArtifactPublic(ArtifactBase):
    id: str

    class Config:
        from_attributes = True


class ArtifactDetail(ArtifactBase):
    id: str
    images: list["ArtifactImage"] = []
    latest_classification: Optional["ClassificationResult"] = None

    class Config:
        from_attributes = True


from app.schemas.image import ArtifactImage
from app.schemas.classification import ClassificationResult
