#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

SKILL_NAME = "harness-preference-extractor"
REPO_ROOT = Path(__file__).resolve().parent
SKILL_SOURCE = REPO_ROOT / "skills" / SKILL_NAME

TARGETS = {
    "claude": Path.home() / ".claude/skills" / SKILL_NAME,
    "codex": Path.home() / ".codex/skills" / SKILL_NAME,
    "pi": Path.home() / ".pi/agent/skills" / SKILL_NAME,
}


def install(target: str) -> None:
    destination = TARGETS[target]
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(SKILL_SOURCE, destination)
    print(f"installed {SKILL_NAME} to {destination}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the harness-preference-extractor skill into a supported local harness skill directory.")
    parser.add_argument("target", choices=sorted(TARGETS), help="Harness target: claude, codex, or pi")
    ns = parser.parse_args()
    install(ns.target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
