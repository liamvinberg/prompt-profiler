from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .handlers import get_handlers
from .models import DetectionResult, PromptRecord
from .profile import build_baseline_instructions, build_candidate_skills, build_preference_cards, build_stack_affinities, build_working_style


def detect_harnesses(home: Path, selected: list[str] | None = None) -> list[DetectionResult]:
    return [handler.detect(home) for handler in get_handlers(selected)]


def extract_records(home: Path, selected: list[str] | None = None) -> list[PromptRecord]:
    records: list[PromptRecord] = []
    for handler in get_handlers(selected):
        records.extend(handler.extract(home))
    records.sort(key=lambda row: (row.timestamp or "", row.harness, row.session_id or ""))
    return records


def build_deduped(rows: list[PromptRecord]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = row.normalized_text
        item = grouped.get(key)
        if item is None:
            grouped[key] = {
                "normalized_text": key,
                "sample_text": row.text,
                "count": 1,
                "first_seen": row.timestamp,
                "last_seen": row.timestamp,
                "harnesses": {row.harness},
                "stores": {row.store},
                "sessions": {row.session_id} if row.session_id else set(),
            }
            continue
        item["count"] += 1
        item["harnesses"].add(row.harness)
        item["stores"].add(row.store)
        if row.session_id:
            item["sessions"].add(row.session_id)
        if row.timestamp and (item["first_seen"] is None or row.timestamp < item["first_seen"]):
            item["first_seen"] = row.timestamp
        if row.timestamp and (item["last_seen"] is None or row.timestamp > item["last_seen"]):
            item["last_seen"] = row.timestamp

    deduped: list[dict[str, Any]] = []
    for item in grouped.values():
        deduped.append(
            {
                "normalized_text": item["normalized_text"],
                "sample_text": item["sample_text"],
                "count": item["count"],
                "first_seen": item["first_seen"],
                "last_seen": item["last_seen"],
                "harnesses": sorted(item["harnesses"]),
                "stores": sorted(item["stores"]),
                "session_count": len(item["sessions"]),
            }
        )
    deduped.sort(key=lambda item: (-item["count"], item["sample_text"]))
    return deduped


def build_outputs(detections: list[DetectionResult], records: list[PromptRecord]) -> dict[str, Any]:
    clean_records = [row for row in records if row.include_cleaned]
    deduped = build_deduped(clean_records)
    stack_affinities = build_stack_affinities(clean_records)
    preference_cards = build_preference_cards(clean_records)
    baseline_instructions = build_baseline_instructions(preference_cards)
    candidate_skills = build_candidate_skills(preference_cards, stack_affinities)
    working_style = build_working_style(preference_cards, stack_affinities)

    by_harness = Counter(row.harness for row in records)
    by_flag = Counter(flag for row in records for flag in row.flags)
    by_store = Counter(row.store for row in records)

    summary = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "counts": {
            "raw_prompts": len(records),
            "clean_prompts": len(clean_records),
            "unique_clean_prompts": len(deduped),
        },
        "supported_harnesses": [detection.harness for detection in detections if detection.supported],
        "by_harness": dict(sorted(by_harness.items())),
        "by_store": dict(sorted(by_store.items())),
        "flags": dict(sorted(by_flag.items())),
        "top_repeated_prompts": deduped[:25],
        "top_preference_cards": [card.to_dict() for card in preference_cards[:15]],
        "top_stack_affinities": dict(list(stack_affinities.items())[:15]),
    }

    return {
        "support_matrix": [detection.to_dict() for detection in detections],
        "raw_prompts": [record.to_dict() for record in records],
        "clean_prompts": [record.to_dict() for record in clean_records],
        "deduped_prompts": deduped,
        "preference_cards": [card.to_dict() for card in preference_cards],
        "stack_affinities": stack_affinities,
        "baseline_instructions": baseline_instructions,
        "candidate_skills": candidate_skills,
        "working_style": working_style,
        "summary": summary,
    }
