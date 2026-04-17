from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .pipeline import build_outputs, detect_harnesses, extract_records


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract and profile local prompts from supported agent harnesses.")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Home directory to inspect (default: current user's home)")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd() / "output", help="Directory where outputs are written")
    parser.add_argument("--harness", action="append", dest="harnesses", help="Specific harness to include. Repeat for multiple harnesses.")
    return parser


def run_detection(args: list[str] | None = None) -> int:
    parser = _build_parser()
    ns = parser.parse_args(args=args)
    detections = detect_harnesses(ns.home, ns.harnesses)
    print(json.dumps([detection.to_dict() for detection in detections], indent=2, ensure_ascii=False))
    return 0


def run_extraction(args: list[str] | None = None) -> int:
    parser = _build_parser()
    ns = parser.parse_args(args=args)
    ns.output_dir.mkdir(parents=True, exist_ok=True)

    detections = detect_harnesses(ns.home, ns.harnesses)
    records = extract_records(ns.home, ns.harnesses)
    outputs = build_outputs(detections, records)

    _write_json(ns.output_dir / "support_matrix.json", outputs["support_matrix"])
    _write_jsonl(ns.output_dir / "raw_prompts.jsonl", outputs["raw_prompts"])
    _write_jsonl(ns.output_dir / "clean_prompts.jsonl", outputs["clean_prompts"])
    _write_jsonl(ns.output_dir / "deduped_prompts.jsonl", outputs["deduped_prompts"])
    _write_jsonl(ns.output_dir / "preference_cards.jsonl", outputs["preference_cards"])
    _write_json(ns.output_dir / "stack_affinities.json", outputs["stack_affinities"])
    (ns.output_dir / "baseline_instructions.md").write_text(outputs["baseline_instructions"], encoding="utf-8")
    (ns.output_dir / "candidate_skills.md").write_text(outputs["candidate_skills"], encoding="utf-8")
    (ns.output_dir / "working_style.md").write_text(outputs["working_style"], encoding="utf-8")
    _write_json(ns.output_dir / "summary.json", outputs["summary"])

    compact = {
        "output_dir": str(ns.output_dir.resolve()),
        "supported_harnesses": outputs["summary"]["supported_harnesses"],
        "counts": outputs["summary"]["counts"],
        "top_stack_affinities": outputs["summary"]["top_stack_affinities"],
    }
    print(json.dumps(compact, indent=2, ensure_ascii=False))
    return 0
