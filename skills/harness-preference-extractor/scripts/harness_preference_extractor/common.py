from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from .models import PromptRecord

SYSTEM_PATTERNS = [
    re.compile(r"^<user_instructions>", re.I),
    re.compile(r"^<environment_context>", re.I),
    re.compile(r"^<system-reminder>", re.I),
    re.compile(r"^\[system reminder", re.I),
    re.compile(r"\[system directive", re.I),
    re.compile(r"^<command-instruction>", re.I),
    re.compile(r"^<session-context>", re.I),
    re.compile(r"^<user-request>", re.I),
    re.compile(r"^\[analyze-mode\]", re.I),
    re.compile(r"OMO_INTERNAL_INITIATOR", re.I),
    re.compile(r"^Continue if you have next steps", re.I),
]

HOUSEKEEPING_EXACT = {
    "continue",
    "alright proceed",
    "proceed",
    "update",
    "yes",
    "ok",
    "okay",
    "thanks",
    "thank you",
    "/clear",
    "/config",
    "/vim",
    "/login",
}

ANGER_PATTERN = re.compile(
    r"\b(fuck(?:ing)?|shit|wtf|idiot|stupid|dumbass|moron|retard(?:ed)?)\b",
    re.I,
)


def collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_for_dedupe(text: str) -> str:
    return collapse_ws(text).lower()


def to_iso_from_epoch(value: Any) -> str | None:
    if value is None:
        return None
    try:
        num = float(value)
    except Exception:
        return str(value)
    if num > 10_000_000_000:
        num /= 1000.0
    return datetime.fromtimestamp(num, tz=timezone.utc).isoformat()


def extract_text_parts(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            if item_type in {"text", "input_text"} and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(part for part in parts if part.strip())
    return ""


def looks_system(text: str) -> bool:
    stripped = text.strip()
    return any(pattern.search(stripped) for pattern in SYSTEM_PATTERNS)


def looks_housekeeping(text: str) -> bool:
    stripped = collapse_ws(text).lower()
    if stripped in HOUSEKEEPING_EXACT:
        return True
    if stripped.startswith("/") and len(stripped.split()) == 1:
        return True
    if len(stripped) <= 24 and stripped.startswith("continue"):
        return True
    return False


def looks_anger(text: str) -> bool:
    return bool(ANGER_PATTERN.search(text))


def preprocess_text(harness: str, text: str) -> str:
    cleaned = text.strip()
    if harness == "opencode":
        cleaned = re.split(r"\nCalled the [A-Za-z_]+ tool with the following input:", cleaned, maxsplit=1)[0]
        cleaned = re.split(r"\nExecuted the [A-Za-z_]+ tool with the following input:", cleaned, maxsplit=1)[0]
    return cleaned.strip()


def build_record(
    *,
    harness: str,
    store: str,
    session_id: str | None,
    timestamp: str | None,
    cwd: str | None,
    source_path: str,
    text: str,
) -> PromptRecord | None:
    cleaned_text = preprocess_text(harness, text)
    if not cleaned_text:
        return None

    flags: list[str] = []
    if looks_system(cleaned_text):
        flags.append("system_like")
    if looks_housekeeping(cleaned_text):
        flags.append("housekeeping")
    if looks_anger(cleaned_text):
        flags.append("anger")
    if len(collapse_ws(cleaned_text)) < 20:
        flags.append("short")

    include_cleaned = not ({"system_like", "housekeeping", "anger"} & set(flags)) and "short" not in flags

    return PromptRecord(
        harness=harness,
        store=store,
        session_id=session_id,
        timestamp=timestamp,
        cwd=cwd,
        source_path=source_path,
        text=cleaned_text,
        normalized_text=normalize_for_dedupe(cleaned_text),
        flags=flags,
        include_cleaned=include_cleaned,
    )


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)
