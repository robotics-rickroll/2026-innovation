from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from starlette.datastructures import UploadFile as StarletteUploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.artifact import Artifact
from app.models.artifact_image import ArtifactImage
from app.models.classification_result import ClassificationResult
from app.models.enums import ClassificationStatus, ProviderName
from app.models.user import User
from app.schemas.artifact import ArtifactCreate, ArtifactDetail, ArtifactUpdate
from app.schemas.classification import ClassificationResult as ClassificationResultSchema, ClassificationUpdate
from app.schemas.image import ArtifactImage as ArtifactImageSchema
from app.schemas.listing import ArtifactListItem
from app.services.ai import get_provider, normalize_classification, status_from_error
from app.services.location import compute_location_approx, haversine_miles
from app.services.storage import save_upload

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


def _latest_classification_subquery(db: Session):
    return (
        db.query(
            ClassificationResult.artifact_id,
            func.max(ClassificationResult.created_at).label("max_created"),
        )
        .group_by(ClassificationResult.artifact_id)
        .subquery()
    )


def _attach_latest(artifact: Artifact, db: Session) -> Optional[ClassificationResult]:
    return (
        db.query(ClassificationResult)
        .filter(ClassificationResult.artifact_id == artifact.id)
        .order_by(ClassificationResult.created_at.desc())
        .first()
    )


def _parse_create_payload(raw: dict[str, Any]) -> ArtifactCreate:
    return ArtifactCreate(**raw)

def _normalize_additional_info(value: Any) -> Optional[dict[str, Any]]:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        normalized: dict[str, Any] = {}
        for item in value:
            if not isinstance(item, dict):
                continue
            key = str(item.get("key", "")).strip()
            if key:
                normalized[key] = item.get("value")
        return normalized
    return {"value": value}


def _build_classification_payload(artifact: Artifact) -> dict[str, Any]:
    image_urls = [img.url for img in artifact.images]
    image_paths: list[str] = []
    for url in image_urls:
        if url.startswith("/uploads/"):
            image_paths.append(str(Path(settings.upload_dir) / Path(url).name))
    return {
        "artifact_id": artifact.artifact_id,
        "timestamp": artifact.timestamp.isoformat(),
        "measurements": {
            "length_cm": artifact.measure_length_cm,
            "width_cm": artifact.measure_width_cm,
            "height_cm": artifact.measure_height_cm,
        },
        "additional_info": artifact.additional_info,
        "image_count": len(image_urls),
        "image_urls": image_urls,
        "image_paths": image_paths,
    }


def _classify_and_store(artifact: Artifact, db: Session) -> ClassificationResult:
    provider = get_provider()
    payload = _build_classification_payload(artifact)
    try:
        raw = provider.classify(payload)
        normalized = normalize_classification(raw)
        status_value = ClassificationStatus(normalized["status"])
        classification = ClassificationResult(
            artifact_id=artifact.id,
            status=status_value,
            summary=normalized.get("summary"),
            artifact_type=normalized.get("artifact_type"),
            civilization=normalized.get("civilization"),
            age_range=normalized.get("age_range"),
            confidence=normalized.get("confidence"),
            raw_response=raw,
            provider=provider.provider_name,
        )
    except Exception:
        raw = status_from_error()
        classification = ClassificationResult(
            artifact_id=artifact.id,
            status=ClassificationStatus.ERROR,
            summary=raw.get("summary"),
            raw_response={"error": "parse_failed"},
            provider=provider.provider_name,
        )
    db.add(classification)
    db.commit()
    db.refresh(classification)
    return classification


@router.get("", response_model=list[ArtifactListItem])
def list_artifacts(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None, alias="type"),
    civilization: Optional[str] = Query(default=None),
    status_filter: Optional[ClassificationStatus] = Query(default=None, alias="status"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    sort: Optional[str] = Query(default=None),
):
    latest_subq = _latest_classification_subquery(db)
    latest_alias = aliased(ClassificationResult)
    query = (
        db.query(Artifact, latest_alias)
        .outerjoin(latest_subq, Artifact.id == latest_subq.c.artifact_id)
        .outerjoin(
            latest_alias,
            (latest_alias.artifact_id == Artifact.id) & (latest_alias.created_at == latest_subq.c.max_created),
        )
    )
    if q:
        query = query.filter(Artifact.artifact_id.ilike(f"%{q}%"))
    if type:
        query = query.filter(latest_alias.artifact_type == type)
    if civilization:
        query = query.filter(latest_alias.civilization == civilization)
    if status_filter:
        query = query.filter(latest_alias.status == status_filter)
    if sort == "timestamp":
        query = query.order_by(Artifact.timestamp.desc())
    elif sort == "artifact_id":
        query = query.order_by(Artifact.artifact_id.asc())
    items = query.offset(offset).limit(limit).all()
    results: list[ArtifactListItem] = []
    for artifact, latest_row in items:
        latest_model = None
        if latest_row:
            latest_model = ClassificationResultSchema.model_validate(latest_row, from_attributes=True)
        results.append(
            ArtifactListItem(
                id=artifact.id,
                artifact_id=artifact.artifact_id,
                timestamp=artifact.timestamp,
                location_approx=artifact.location_approx,
                latest_classification=latest_model,
            )
        )
    return results


@router.get("/{artifact_id}", response_model=ArtifactDetail)
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    latest = _attach_latest(artifact, db)
    return ArtifactDetail(
        id=artifact.id,
        artifact_id=artifact.artifact_id,
        timestamp=artifact.timestamp,
        location_approx=artifact.location_approx,
        measure_length_cm=artifact.measure_length_cm,
        measure_width_cm=artifact.measure_width_cm,
        measure_height_cm=artifact.measure_height_cm,
        additional_info=artifact.additional_info,
        images=[ArtifactImageSchema.model_validate(img, from_attributes=True) for img in artifact.images],
        latest_classification=(
            ClassificationResultSchema.model_validate(latest, from_attributes=True) if latest else None
        ),
    )


@router.get("/{artifact_id}/images", response_model=list[ArtifactImageSchema])
def get_images(artifact_id: str, db: Session = Depends(get_db)):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return [ArtifactImageSchema.model_validate(img, from_attributes=True) for img in artifact.images]


@router.get("/{artifact_id}/classification", response_model=Optional[ClassificationResultSchema])
def get_classification(artifact_id: str, db: Session = Depends(get_db)):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    latest = _attach_latest(artifact, db)
    if not latest:
        return None
    return ClassificationResultSchema.model_validate(latest, from_attributes=True)


@router.post("", response_model=ArtifactDetail, status_code=status.HTTP_201_CREATED)
async def create_artifact(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content_type = request.headers.get("content-type", "")
    images: list[str] = []
    if "multipart/form-data" in content_type:
        form = await request.form()
        metadata_raw = form.get("metadata")
        if not metadata_raw:
            raise HTTPException(status_code=400, detail="metadata is required")
        try:
            payload = json.loads(metadata_raw)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON") from exc
        files = form.getlist("files")
        print(f"Received {len(files)} files")
        #print file details
        print("Files details:")
        print(files)
        for item in files:
            if isinstance(item, (UploadFile, StarletteUploadFile)):
                images.append(save_upload(item))
            else:
                raise HTTPException(status_code=400, detail="Invalid file upload")
        payload["image_urls"] = images
    else:
        payload = await request.json()
    if "additional_info" in payload:
        payload["additional_info"] = _normalize_additional_info(payload.get("additional_info"))
    data = _parse_create_payload(payload)
    location_approx = compute_location_approx(data.location_lat, data.location_lng)
    artifact = Artifact(
        artifact_id=data.artifact_id,
        timestamp=data.timestamp or datetime.utcnow(),
        location_lat=data.location_lat,
        location_lng=data.location_lng,
        location_approx=location_approx,
        measure_length_cm=data.measure_length_cm,
        measure_width_cm=data.measure_width_cm,
        measure_height_cm=data.measure_height_cm,
        additional_info=data.additional_info,
    )
    db.add(artifact)
    db.flush()
    for url in data.image_urls:
        db.add(ArtifactImage(artifact_id=artifact.id, url=url))
    db.commit()
    db.refresh(artifact)
    _classify_and_store(artifact, db)
    if len(data.image_urls) < 5:
        print("Warning: fewer than 5 images submitted")
    return get_artifact(artifact.id, db)


@router.put("/{artifact_id}", response_model=ArtifactDetail)
def update_artifact(
    artifact_id: str,
    payload: ArtifactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(artifact, field, value)
    if payload.location_lat is not None or payload.location_lng is not None:
        artifact.location_approx = compute_location_approx(artifact.location_lat, artifact.location_lng)
    db.commit()
    db.refresh(artifact)
    return get_artifact(artifact.id, db)


@router.put("/{artifact_id}/classification", response_model=ClassificationResultSchema)
def override_classification(
    artifact_id: str,
    payload: ClassificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    latest = _attach_latest(artifact, db)
    if not latest:
        latest = ClassificationResult(artifact_id=artifact.id, provider=ProviderName.mock)
        db.add(latest)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(latest, field, value)
    db.commit()
    db.refresh(latest)
    print(f"Classification overridden for artifact {artifact.artifact_id}")
    return ClassificationResultSchema.model_validate(latest, from_attributes=True)


@router.post("/{artifact_id}/classify", response_model=ClassificationResultSchema)
def classify_artifact(
    artifact_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    classification = _classify_and_store(artifact, db)
    return ClassificationResultSchema.model_validate(classification, from_attributes=True)


@router.get("/{artifact_id}/nearby", response_model=list[ArtifactListItem])
def nearby_artifacts(
    artifact_id: str,
    radius_miles: float = Query(default=15, ge=1),
    db: Session = Depends(get_db),
):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if artifact.location_lat is None or artifact.location_lng is None:
        return []
    candidates = db.query(Artifact).filter(Artifact.id != artifact.id).all()
    results: list[ArtifactListItem] = []
    for candidate in candidates:
        if candidate.location_lat is None or candidate.location_lng is None:
            continue
        distance = haversine_miles(
            artifact.location_lat,
            artifact.location_lng,
            candidate.location_lat,
            candidate.location_lng,
        )
        if distance <= radius_miles:
            latest = _attach_latest(candidate, db)
            results.append(
                ArtifactListItem(
                    id=candidate.id,
                    artifact_id=candidate.artifact_id,
                    timestamp=candidate.timestamp,
                    location_approx=candidate.location_approx,
                    latest_classification=(
                        ClassificationResultSchema.model_validate(latest, from_attributes=True)
                        if latest
                        else None
                    ),
                )
            )
    return results
