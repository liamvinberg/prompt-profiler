from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "skills" / "prompt-profiler" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from harness_preference_extractor.handlers import ClaudeCodeHandler, CodexHandler, CursorHandler, OpenCodeHandler, PiHandler


class HandlerTests(unittest.TestCase):
    def test_handlers_extract_records_from_supported_stores(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            self._write_claude(home)
            self._write_codex(home)
            self._write_cursor(home)
            self._write_pi(home)
            self._write_opencode(home)

            claude_records = ClaudeCodeHandler().extract(home)
            codex_records = CodexHandler().extract(home)
            cursor_records = CursorHandler().extract(home)
            pi_records = PiHandler().extract(home)
            opencode_records = OpenCodeHandler().extract(home)

            self.assertEqual(len(claude_records), 1)
            self.assertEqual(len(codex_records), 1)
            self.assertEqual(len(cursor_records), 2)
            self.assertEqual(len(pi_records), 1)
            self.assertEqual(len(opencode_records), 1)

            self.assertIn("atomic commits", claude_records[0].text.lower())
            self.assertIn("official docs", codex_records[0].text.lower())
            self.assertIn("expo", cursor_records[0].text.lower())
            self.assertIn("architecture", pi_records[0].text.lower())
            self.assertIn("next.js", opencode_records[0].text.lower())

    def _write_claude(self, home: Path) -> None:
        path = home / ".claude/transcripts/session-1.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"type": "user", "timestamp": "2026-04-17T00:00:00Z", "content": "Prefer atomic commits"}
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    def _write_codex(self, home: Path) -> None:
        path = home / ".codex/history.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"ts": 1710000000, "session_id": "codex-session", "text": "Check official docs first"}
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    def _write_cursor(self, home: Path) -> None:
        path = home / ".cursor/prompt_history.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(["Use Expo for mobile", "Keep the structure maintainable"]), encoding="utf-8")

    def _write_pi(self, home: Path) -> None:
        path = home / ".pi/agent/sessions/project/session.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            {"type": "session", "id": "pi-session", "cwd": "/tmp/project"},
            {
                "type": "message",
                "timestamp": "2026-04-17T00:00:00Z",
                "message": {"role": "user", "content": [{"type": "text", "text": "Prefer architecture first"}]},
            },
        ]
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    def _write_opencode(self, home: Path) -> None:
        path = home / ".local/share/opencode/opencode.db"
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
        try:
            conn.execute("CREATE TABLE project (id TEXT PRIMARY KEY, worktree TEXT)")
            conn.execute("CREATE TABLE session (id TEXT PRIMARY KEY, project_id TEXT)")
            conn.execute("CREATE TABLE message (id TEXT PRIMARY KEY, session_id TEXT, time_created INTEGER, data TEXT)")
            conn.execute("CREATE TABLE part (id TEXT PRIMARY KEY, message_id TEXT, time_created INTEGER, data TEXT)")
            conn.execute("INSERT INTO project (id, worktree) VALUES (?, ?)", ("project-1", "/tmp/opencode"))
            conn.execute("INSERT INTO session (id, project_id) VALUES (?, ?)", ("session-1", "project-1"))
            conn.execute(
                "INSERT INTO message (id, session_id, time_created, data) VALUES (?, ?, ?, ?)",
                ("message-1", "session-1", 1710000000000, json.dumps({"role": "user"})),
            )
            conn.execute(
                "INSERT INTO part (id, message_id, time_created, data) VALUES (?, ?, ?, ?)",
                ("part-1", "message-1", 1710000000000, json.dumps({"type": "text", "text": "Use Next.js and keep it simple"})),
            )
            conn.commit()
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
