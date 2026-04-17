from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "skills" / "harness-preference-extractor" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from harness_preference_extractor.common import build_record
from harness_preference_extractor.profile import build_baseline_instructions, build_candidate_skills, build_preference_cards, build_stack_affinities


class ProfileTests(unittest.TestCase):
    def test_profile_outputs_infer_preferences_and_skill_candidates(self) -> None:
        texts = [
            "Set the architecture first and keep the foundation clean.",
            "Start with the architecture and get the foundation right before features.",
            "Check official docs before choosing the framework.",
            "Use the official docs and best practices first.",
            "Do not overengineer this. Keep it straightforward.",
            "Make atomic commits and keep them small.",
            "Use Next.js, React, Tailwind, shadcn, Drizzle, and Better Auth.",
            "Use Expo and React Native for the mobile app.",
            "We should compare the sibling repo before implementing this.",
            "Use the upstream repo as a reference before changing our code.",
        ]
        records = [
            build_record(
                harness="codex",
                store="store",
                session_id=str(index),
                timestamp=None,
                cwd=None,
                source_path="/tmp/store",
                text=text,
            )
            for index, text in enumerate(texts)
        ]
        clean_records = [record for record in records if record is not None and record.include_cleaned]

        cards = build_preference_cards(clean_records)
        affinities = build_stack_affinities(clean_records)
        baseline = build_baseline_instructions(cards)
        candidate_skills = build_candidate_skills(cards, affinities)

        labels = {card.label for card in cards}
        self.assertIn("Prefers architecture-first setup before feature work", labels)
        self.assertIn("Prefers checking official docs for framework or library decisions", labels)
        self.assertIn("Prefers straightforward implementations and dislikes overengineering", labels)
        self.assertIn("nextjs", affinities)
        self.assertIn("expo", affinities)
        self.assertIn("architecture-first", baseline.lower())
        self.assertIn("web-foundation", candidate_skills)
        self.assertIn("mobile-foundation", candidate_skills)
        self.assertIn("repo-reference", candidate_skills)


if __name__ == "__main__":
    unittest.main()
