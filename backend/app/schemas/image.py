from __future__ import annotations
from datetime import datetime

from pydantic import BaseModel


class ArtifactImage(BaseModel):
    id: str
    url: str
    created_at: datetime

    class Config:
        from_attributes = True
