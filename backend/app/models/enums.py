from __future__ import annotations
import enum


class ClassificationStatus(str, enum.Enum):
    CLASSIFIED = "CLASSIFIED"
    NOT_CLASSIFIABLE = "NOT_CLASSIFIABLE"
    PENDING = "PENDING"
    ERROR = "ERROR"


class ProviderName(str, enum.Enum):
    mock = "mock"
    openai = "openai"
    gemini = "gemini"


class UserRole(str, enum.Enum):
    ARCHAEOLOGIST = "ARCHAEOLOGIST"
