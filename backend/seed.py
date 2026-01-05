from __future__ import annotations
from datetime import datetime

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.artifact import Artifact
from app.models.artifact_image import ArtifactImage
from app.models.classification_result import ClassificationResult
from app.models.enums import ClassificationStatus, ProviderName
from app.models.user import User
from app.services.location import compute_location_approx


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "arch@example.com").first():
            user = User(email="arch@example.com", password_hash=get_password_hash("password"))
            db.add(user)

        if db.query(Artifact).count() == 0:
            artifact = Artifact(
                artifact_id="ART-000123",
                timestamp=datetime.utcnow(),
                location_lat=34.05,
                location_lng=-118.25,
                location_approx=compute_location_approx(34.05, -118.25),
                measure_length_cm=10.2,
                measure_width_cm=5.1,
                measure_height_cm=2.3,
                additional_info={"material_guess": "ceramic", "shape": "fragment"},
            )
            db.add(artifact)
            db.flush()
            for idx in range(1, 6):
                db.add(ArtifactImage(artifact_id=artifact.id, url=f"https://example.com/{idx}.jpg"))
            db.add(
                ClassificationResult(
                    artifact_id=artifact.id,
                    status=ClassificationStatus.CLASSIFIED,
                    summary="Ceramic shard with tooling marks.",
                    artifact_type="Ceramic shard",
                    civilization="Unknown local culture",
                    age_range="500-300 BCE",
                    confidence=0.74,
                    raw_response={"seed": True},
                    provider=ProviderName.mock,
                )
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
