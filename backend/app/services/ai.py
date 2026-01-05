from __future__ import annotations
import json
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import settings
from app.models.enums import ClassificationStatus, ProviderName


class AIProvider(ABC):
    provider_name: ProviderName

    @abstractmethod
    def classify(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class MockProvider(AIProvider):
    provider_name = ProviderName.mock

    def classify(self, payload: dict[str, Any]) -> dict[str, Any]:
        artifact_id = payload.get("artifact_id", "")
        if artifact_id.endswith("5"):
            return {
                "status": "NOT_CLASSIFIABLE",
                "summary": "Surface erosion prevents reliable identification.",
                "artifact_type": None,
                "civilization": None,
                "age_range": None,
                "confidence": 0.0,
            }
        return {
            "status": "CLASSIFIED",
            "summary": "Likely a ceramic vessel fragment with simple tooling marks.",
            "artifact_type": "Ceramic shard",
            "civilization": "Unknown local culture",
            "age_range": "500-300 BCE",
            "confidence": 0.74,
        }


class OpenAIProvider(AIProvider):
    provider_name = ProviderName.openai

    def classify(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set")
        prompt = _build_prompt(payload)
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        body = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are an expert artifact classifier."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        resp = httpx.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers, timeout=30)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return _parse_model_json(content)


class GeminiProvider(AIProvider):
    provider_name = ProviderName.gemini

    def classify(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set")
        prompt = _build_prompt(payload)
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-1.5-flash:generateContent"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }
        resp = httpx.post(f"{url}?key={settings.gemini_api_key}", json=body, timeout=30)
        resp.raise_for_status()
        content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_model_json(content)


def _build_prompt(payload: dict[str, Any]) -> str:
    return (
        "Return STRICT JSON with keys: status, summary, artifact_type, civilization, age_range, confidence. "
        "status must be CLASSIFIED or NOT_CLASSIFIABLE.\n\nArtifact payload:\n"
        f"{json.dumps(payload)}"
    )


def _parse_model_json(content: str) -> dict[str, Any]:
    data = json.loads(content)
    return data


def get_provider() -> AIProvider:
    provider = settings.ai_provider.lower()
    if provider == "openai":
        return OpenAIProvider()
    if provider == "gemini":
        return GeminiProvider()
    return MockProvider()


def normalize_classification(data: dict[str, Any]) -> dict[str, Any]:
    status = data.get("status")
    if status not in {"CLASSIFIED", "NOT_CLASSIFIABLE"}:
        raise ValueError("Invalid status")
    return {
        "status": status,
        "summary": data.get("summary"),
        "artifact_type": data.get("artifact_type"),
        "civilization": data.get("civilization"),
        "age_range": data.get("age_range"),
        "confidence": data.get("confidence"),
    }


def status_from_error() -> dict[str, Any]:
    return {
        "status": ClassificationStatus.ERROR.value,
        "summary": "Classification failed.",
        "artifact_type": None,
        "civilization": None,
        "age_range": None,
        "confidence": None,
    }
