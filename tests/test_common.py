from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "skills" / "harness-preference-extractor" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from harness_preference_extractor.common import build_record


class CommonTests(unittest.TestCase):
    def test_opencode_preprocess_strips_tool_expansion(self) -> None:
        record = build_record(
            harness="opencode",
            store="store",
            session_id="s1",
            timestamp=None,
            cwd=None,
            source_path="/tmp/store",
            text="Use Next.js and keep it simple\nCalled the Read tool with the following input:\n<file>huge dump</file>",
        )
        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.text, "Use Next.js and keep it simple")

    def test_flags_housekeeping_system_and_anger(self) -> None:
        housekeeping = build_record(
            harness="codex",
            store="store",
            session_id=None,
            timestamp=None,
            cwd=None,
            source_path="/tmp/store",
            text="continue",
        )
        system_like = build_record(
            harness="codex",
            store="store",
            session_id=None,
            timestamp=None,
            cwd=None,
            source_path="/tmp/store",
            text="<user_instructions>keep this</user_instructions>",
        )
        anger = build_record(
            harness="codex",
            store="store",
            session_id=None,
            timestamp=None,
            cwd=None,
            source_path="/tmp/store",
            text="this is fucking broken",
        )
        self.assertIn("housekeeping", housekeeping.flags)
        self.assertIn("system_like", system_like.flags)
        self.assertIn("anger", anger.flags)
        self.assertFalse(housekeeping.include_cleaned)
        self.assertFalse(system_like.include_cleaned)
        self.assertFalse(anger.include_cleaned)


if __name__ == "__main__":
    unittest.main()
