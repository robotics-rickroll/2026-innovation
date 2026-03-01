from __future__ import annotations
import os
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


def ensure_upload_dir() -> Path:
    path = Path(settings.upload_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload(file: UploadFile) -> str:
    upload_dir = ensure_upload_dir()
    suffix = Path(file.filename).suffix
    name = f"{uuid4().hex}{suffix}"
    dest = upload_dir / name
    #print details 
    print(f"Saving upload to: {dest}")
    

    with dest.open("wb") as buffer:
        buffer.write(file.file.read())
        print(f"Saved to: {dest}")
    return f"/uploads/{name}"
