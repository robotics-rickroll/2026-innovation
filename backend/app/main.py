from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app import models

app = FastAPI(title="Artifact Classification API")

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
allow_origins = ["*"] if "*" in origins else origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(api_router)

app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
