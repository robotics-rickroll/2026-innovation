from __future__ import annotations
from app.models.enums import ClassificationStatus


def test_location_privacy(client, auth_headers, sample_artifact_payload):
    create = client.post("/api/artifacts", json=sample_artifact_payload, headers=auth_headers)
    assert create.status_code == 201
    artifact_id = create.json()["id"]

    list_resp = client.get("/api/artifacts")
    assert list_resp.status_code == 200
    assert "location_lat" not in list_resp.text
    assert "location_lng" not in list_resp.text

    detail = client.get(f"/api/artifacts/{artifact_id}")
    assert detail.status_code == 200
    assert "location_lat" not in detail.text
    assert "location_lng" not in detail.text


def test_create_and_classify_happy_path(client, auth_headers, sample_artifact_payload):
    create = client.post("/api/artifacts", json=sample_artifact_payload, headers=auth_headers)
    assert create.status_code == 201
    artifact_id = create.json()["id"]

    classify = client.post(f"/api/artifacts/{artifact_id}/classify", headers=auth_headers)
    assert classify.status_code == 200
    assert classify.json()["status"] in {
        ClassificationStatus.CLASSIFIED.value,
        ClassificationStatus.NOT_CLASSIFIABLE.value,
    }


def test_auth_required_for_edit(client, auth_headers, sample_artifact_payload):
    create = client.post("/api/artifacts", json=sample_artifact_payload, headers=auth_headers)
    assert create.status_code == 201
    artifact_id = create.json()["id"]

    update = client.put(
        f"/api/artifacts/{artifact_id}",
        json={"measure_length_cm": 99},
    )
    assert update.status_code == 401


def test_not_classifiable(client, auth_headers, sample_artifact_payload):
    payload = sample_artifact_payload.copy()
    payload["artifact_id"] = "ART-000125"
    create = client.post("/api/artifacts", json=payload, headers=auth_headers)
    assert create.status_code == 201
    artifact_id = create.json()["id"]

    classify = client.post(f"/api/artifacts/{artifact_id}/classify", headers=auth_headers)
    assert classify.status_code == 200
    assert classify.json()["status"] == ClassificationStatus.NOT_CLASSIFIABLE.value
