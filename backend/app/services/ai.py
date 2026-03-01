from __future__ import annotations
import json
from abc import ABC, abstractmethod
import base64
import mimetypes
from pathlib import Path
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
        parts: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for url in payload.get("image_urls", []) or []:
            if isinstance(url, str) and url.startswith("http"):
                parts.append({"type": "image_url", "image_url": {"url": url}})
        for path in payload.get("image_paths", []) or []:
            if isinstance(path, str):
                data_url = _data_url_from_path(path)
                if data_url:
                    parts.append({"type": "image_url", "image_url": {"url": data_url}})
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        print("OpenAI request model=gpt-4o-mini")
        print(f"OpenAI request payload keys: {list(payload.keys())}")
        print(f"OpenAI request images: {len(parts) - 1}")
        body = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are an expert artifact classifier."},
                {"role": "user", "content": parts},
            ],
            "temperature": 0.2,
        }
        resp = httpx.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers, timeout=30)
        print(f"OpenAI response status: {resp.status_code}")
        print(f"OpenAI response body: {resp.text}")
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return _parse_model_json(content)


class GeminiProvider(AIProvider):
    provider_name = ProviderName.gemini

    def classify(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set")
        prompt = _build_prompt(payload)
        parts: list[dict[str, Any]] = [{"text": prompt}]
        for path in payload.get("image_paths", []) or []:
            if isinstance(path, str):
                inline_data = _inline_data_from_path(path)
                if inline_data:
                    parts.append({"inline_data": inline_data})
        model = settings.gemini_model
        api_version = "v1beta" if "preview" in model or "exp" in model else "v1"
        url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model}:generateContent"
        body = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"temperature": 0.2},
        }
        headers = {"x-goog-api-key": settings.gemini_api_key}
        print(f"Gemini request url: {url}")
        print(f"Gemini request payload keys: {list(payload.keys())}")
        print(f"Gemini request images: {len(parts) - 1}")
        resp = httpx.post(url, json=body, headers=headers, timeout=30)
        print(f"Gemini response status: {resp.status_code}")
        print(f"Gemini response body: {resp.text}")
        resp.raise_for_status()
        content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_model_json(content)


def _build_prompt(payload: dict[str, Any]) -> str:
    return (
        "You will be given one or more artifact images plus metadata. "
        "Identify what the object is and compare it to known archaeological artifacts. The summary should not say what it is, instead suggest potential identifications based on features. "        "Return STRICT JSON with keys: status, summary, artifact_type, civilization, age_range, confidence. "
        "status must be CLASSIFIED or NOT_CLASSIFIABLE. "
        "If the images are unclear or insufficient, return NOT_CLASSIFIABLE with a brief reason in summary.\n\n"
        "Artifact payload:\n"
        f"{json.dumps(payload)}"
    )


def _parse_model_json(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(cleaned[start : end + 1])
            raise


def _data_url_from_path(path: str) -> str | None:
    file_path = Path(path)
    if not file_path.exists():
        return None
    mime_type, _ = mimetypes.guess_type(file_path.name)
    if not mime_type:
        mime_type = "application/octet-stream"
    encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _inline_data_from_path(path: str) -> dict[str, str] | None:
    file_path = Path(path)
    if not file_path.exists():
        return None
    mime_type, _ = mimetypes.guess_type(file_path.name)
    if not mime_type:
        mime_type = "application/octet-stream"
    encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
    return {"mime_type": mime_type, "data": encoded}


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
