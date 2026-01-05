from __future__ import annotations
import os
from uuid import uuid4
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.api import deps
from app.main import app
from app.models.user import User

TEST_DB_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, future=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture()
def db_session(engine):
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture()
def client(db_session, monkeypatch):
    def override_get_db():
        yield db_session

    app.dependency_overrides = {}
    app.dependency_overrides[deps.get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture()
def test_user(db_session):
    user = db_session.query(User).filter(User.email == "arch@example.com").first()
    if user:
        return user
    user = User(email="arch@example.com", password_hash=get_password_hash("password"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def auth_headers(client, test_user):
    resp = client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_artifact_payload():
    return {
        "artifact_id": f"ART-{uuid4().hex[:6]}",
        "timestamp": datetime.utcnow().isoformat(),
        "location_lat": 34.05,
        "location_lng": -118.25,
        "measure_length_cm": 10.0,
        "measure_width_cm": 5.0,
        "measure_height_cm": 2.0,
        "additional_info": {"material_guess": "ceramic"},
        "image_urls": [
            "https://example.com/1.jpg",
            "https://example.com/2.jpg",
            "https://example.com/3.jpg",
            "https://example.com/4.jpg",
            "https://example.com/5.jpg",
        ],
    }
