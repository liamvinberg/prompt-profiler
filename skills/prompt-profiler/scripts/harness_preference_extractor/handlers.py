from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from .common import build_record, extract_text_parts, to_iso_from_epoch
from .models import DetectionResult, PromptRecord, StoreInfo, resolve_path


class HarnessHandler(ABC):
    name: str
    store_label: str

    @abstractmethod
    def detect(self, home: Path) -> DetectionResult:
        raise NotImplementedError

    @abstractmethod
    def extract(self, home: Path) -> list[PromptRecord]:
        raise NotImplementedError


class OpenCodeHandler(HarnessHandler):
    name = "opencode"
    store_label = "~/.local/share/opencode/opencode.db"

    def detect(self, home: Path) -> DetectionResult:
        db_path = home / ".local/share/opencode/opencode.db"
        if not db_path.exists():
            return DetectionResult(self.name, False, "store not found", [])
        return DetectionResult(
            self.name,
            True,
            "supported store found",
            [
                StoreInfo(
                    harness=self.name,
                    store=self.store_label,
                    format="sqlite",
                    source_path=resolve_path(db_path),
                    notes="Prompt text comes from message + part tables. User messages are filtered by role.",
                )
            ],
        )

    def extract(self, home: Path) -> list[PromptRecord]:
        db_path = home / ".local/share/opencode/opencode.db"
        if not db_path.exists():
            return []
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        query = """
            SELECT
                m.id AS message_id,
                m.session_id AS session_id,
                m.time_created AS time_created,
                p.worktree AS worktree,
                (
                    SELECT group_concat(text_piece, '\n')
                    FROM (
                        SELECT json_extract(pt.data, '$.text') AS text_piece
                        FROM part pt
                        WHERE pt.message_id = m.id
                          AND json_extract(pt.data, '$.type') = 'text'
                          AND json_extract(pt.data, '$.text') IS NOT NULL
                        ORDER BY pt.time_created, pt.id
                    )
                ) AS text
            FROM message m
            LEFT JOIN session s ON s.id = m.session_id
            LEFT JOIN project p ON p.id = s.project_id
            WHERE json_extract(m.data, '$.role') = 'user'
              AND EXISTS (
                  SELECT 1
                  FROM part pt2
                  WHERE pt2.message_id = m.id
                    AND json_extract(pt2.data, '$.type') = 'text'
              )
            ORDER BY m.time_created
        """
        records: list[PromptRecord] = []
        try:
            for row in conn.execute(query):
                record = build_record(
                    harness=self.name,
                    store=self.store_label,
                    session_id=row["session_id"],
                    timestamp=to_iso_from_epoch(row["time_created"]),
                    cwd=row["worktree"],
                    source_path=resolve_path(db_path),
                    text=row["text"] or "",
                )
                if record:
                    records.append(record)
        finally:
            conn.close()
        return records


class ClaudeCodeHandler(HarnessHandler):
    name = "claude_code"
    store_label = "~/.claude/transcripts/*.jsonl"

    def detect(self, home: Path) -> DetectionResult:
        root = home / ".claude/transcripts"
        files = sorted(root.glob("*.jsonl")) if root.exists() else []
        if not files:
            return DetectionResult(self.name, False, "transcript jsonl files not found", [])
        return DetectionResult(
            self.name,
            True,
            "supported transcript files found",
            [
                StoreInfo(
                    harness=self.name,
                    store=self.store_label,
                    format="jsonl",
                    source_path=resolve_path(root),
                    notes="User prompts are transcript lines where type == user.",
                )
            ],
        )

    def extract(self, home: Path) -> list[PromptRecord]:
        root = home / ".claude/transcripts"
        records: list[PromptRecord] = []
        if not root.exists():
            return records
        for path in sorted(root.glob("*.jsonl")):
            session_id = path.stem
            with path.open() as fh:
                for raw_line in fh:
                    raw_line = raw_line.strip()
                    if not raw_line:
                        continue
                    data = json.loads(raw_line)
                    if data.get("type") != "user":
                        continue
                    content = data.get("content")
                    text = content if isinstance(content, str) else extract_text_parts(content)
                    record = build_record(
                        harness=self.name,
                        store=self.store_label,
                        session_id=session_id,
                        timestamp=data.get("timestamp"),
                        cwd=None,
                        source_path=resolve_path(path),
                        text=text,
                    )
                    if record:
                        records.append(record)
        return records


class CodexHandler(HarnessHandler):
    name = "codex"
    store_label = "~/.codex/history.jsonl"

    def detect(self, home: Path) -> DetectionResult:
        path = home / ".codex/history.jsonl"
        if not path.exists():
            return DetectionResult(self.name, False, "history jsonl not found", [])
        return DetectionResult(
            self.name,
            True,
            "supported history file found",
            [
                StoreInfo(
                    harness=self.name,
                    store=self.store_label,
                    format="jsonl",
                    source_path=resolve_path(path),
                    notes="One JSON object per prompt entry. This is the cleanest codex prompt surface.",
                )
            ],
        )

    def extract(self, home: Path) -> list[PromptRecord]:
        path = home / ".codex/history.jsonl"
        if not path.exists():
            return []
        records: list[PromptRecord] = []
        with path.open() as fh:
            for raw_line in fh:
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                data = json.loads(raw_line)
                text = data.get("text")
                if not isinstance(text, str):
                    continue
                record = build_record(
                    harness=self.name,
                    store=self.store_label,
                    session_id=data.get("session_id"),
                    timestamp=to_iso_from_epoch(data.get("ts")),
                    cwd=None,
                    source_path=resolve_path(path),
                    text=text,
                )
                if record:
                    records.append(record)
        return records


class CursorHandler(HarnessHandler):
    name = "cursor"
    store_label = "~/.cursor/prompt_history.json"

    def detect(self, home: Path) -> DetectionResult:
        path = home / ".cursor/prompt_history.json"
        if not path.exists():
            return DetectionResult(self.name, False, "prompt history file not found", [])
        return DetectionResult(
            self.name,
            True,
            "supported prompt history file found",
            [
                StoreInfo(
                    harness=self.name,
                    store=self.store_label,
                    format="json",
                    source_path=resolve_path(path),
                    notes="Simple JSON array of prompt strings. Metadata is limited but extraction is stable.",
                )
            ],
        )

    def extract(self, home: Path) -> list[PromptRecord]:
        path = home / ".cursor/prompt_history.json"
        if not path.exists():
            return []
        data = json.loads(path.read_text())
        records: list[PromptRecord] = []
        for index, item in enumerate(data):
            if not isinstance(item, str):
                continue
            record = build_record(
                harness=self.name,
                store=self.store_label,
                session_id=f"prompt-history-{index}",
                timestamp=None,
                cwd=None,
                source_path=resolve_path(path),
                text=item,
            )
            if record:
                records.append(record)
        return records


class PiHandler(HarnessHandler):
    name = "pi"
    store_label = "~/.pi/agent/sessions/*/*.jsonl"

    def detect(self, home: Path) -> DetectionResult:
        root = home / ".pi/agent/sessions"
        files = list(self._iter_files(root)) if root.exists() else []
        if not files:
            return DetectionResult(self.name, False, "session jsonl files not found", [])
        return DetectionResult(
            self.name,
            True,
            "supported pi session files found",
            [
                StoreInfo(
                    harness=self.name,
                    store=self.store_label,
                    format="jsonl",
                    source_path=resolve_path(root),
                    notes="Prompt lines are entries where type == message and message.role == user.",
                )
            ],
        )

    def extract(self, home: Path) -> list[PromptRecord]:
        root = home / ".pi/agent/sessions"
        records: list[PromptRecord] = []
        if not root.exists():
            return records
        for path in self._iter_files(root):
            session_id: str | None = None
            cwd: str | None = None
            with path.open() as fh:
                for raw_line in fh:
                    raw_line = raw_line.strip()
                    if not raw_line:
                        continue
                    data = json.loads(raw_line)
                    if data.get("type") == "session":
                        session_id = data.get("id") or session_id
                        cwd = data.get("cwd") or cwd
                        continue
                    if data.get("type") != "message":
                        continue
                    message = data.get("message") or {}
                    if message.get("role") != "user":
                        continue
                    text = extract_text_parts(message.get("content"))
                    record = build_record(
                        harness=self.name,
                        store=self.store_label,
                        session_id=session_id,
                        timestamp=data.get("timestamp") or message.get("timestamp"),
                        cwd=cwd,
                        source_path=resolve_path(path),
                        text=text,
                    )
                    if record:
                        records.append(record)
        return records

    @staticmethod
    def _iter_files(root: Path) -> Iterable[Path]:
        yield from sorted(root.glob("*/*.jsonl"))


SUPPORTED_HANDLERS: list[HarnessHandler] = [
    OpenCodeHandler(),
    ClaudeCodeHandler(),
    CodexHandler(),
    CursorHandler(),
    PiHandler(),
]


def get_handlers(selected: list[str] | None = None) -> list[HarnessHandler]:
    if not selected:
        return SUPPORTED_HANDLERS
    selected_set = {item.strip().lower() for item in selected}
    return [handler for handler in SUPPORTED_HANDLERS if handler.name in selected_set]
