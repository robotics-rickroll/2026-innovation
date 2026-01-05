from __future__ import annotations
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.classification import ClassificationResult


class ArtifactListItem(BaseModel):
    id: str
    artifact_id: str
    timestamp: datetime
    location_approx: Optional[str] = None
    latest_classification: Optional[ClassificationResult] = None

    class Config:
        from_attributes = True
