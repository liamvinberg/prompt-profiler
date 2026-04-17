from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class StoreInfo:
    harness: str
    store: str
    format: str
    source_path: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DetectionResult:
    harness: str
    supported: bool
    reason: str
    stores: list[StoreInfo]

    def to_dict(self) -> dict[str, Any]:
        return {
            "harness": self.harness,
            "supported": self.supported,
            "reason": self.reason,
            "stores": [store.to_dict() for store in self.stores],
        }


@dataclass
class PromptRecord:
    harness: str
    store: str
    session_id: str | None
    timestamp: str | None
    cwd: str | None
    source_path: str
    text: str
    normalized_text: str
    flags: list[str]
    include_cleaned: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PreferenceCard:
    category: str
    key: str
    label: str
    count: int
    confidence: str
    evidence: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def resolve_path(path: Path) -> str:
    return str(path.expanduser().resolve()) if path.exists() else str(path.expanduser())
