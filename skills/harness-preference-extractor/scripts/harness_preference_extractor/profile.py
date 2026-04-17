from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .models import PreferenceCard, PromptRecord

LIBRARY_PATTERNS = {
    "nextjs": re.compile(r"\bnext(?:\.js|js)?\b", re.I),
    "react": re.compile(r"\breact\b", re.I),
    "react-native": re.compile(r"\breact native\b", re.I),
    "expo": re.compile(r"\bexpo\b", re.I),
    "tailwind": re.compile(r"\btailwind\b", re.I),
    "shadcn": re.compile(r"\bshadcn\b", re.I),
    "better-auth": re.compile(r"\bbetter auth\b|\bbetter-auth\b", re.I),
    "supabase": re.compile(r"\bsupabase\b", re.I),
    "trpc": re.compile(r"\bt\s?rpc\b|\btrpc\b", re.I),
    "zod": re.compile(r"\bzod\b", re.I),
    "drizzle": re.compile(r"\bdrizzle\b", re.I),
    "prisma": re.compile(r"\bprisma\b", re.I),
    "bun": re.compile(r"\bbun\b", re.I),
    "vercel": re.compile(r"\bvercel\b", re.I),
    "railway": re.compile(r"\brailway\b", re.I),
    "posthog": re.compile(r"\bposthog\b", re.I),
    "firebase": re.compile(r"\bfirebase\b", re.I),
    "postgres": re.compile(r"\bpostgres(?:ql)?\b", re.I),
    "docker": re.compile(r"\bdocker\b", re.I),
    "python": re.compile(r"\bpython\b", re.I),
    "go": re.compile(r"\bgo\b", re.I),
    "rust": re.compile(r"\brust\b", re.I),
}


@dataclass(frozen=True)
class PreferenceRule:
    category: str
    key: str
    label: str
    pattern: re.Pattern[str]
    baseline: bool = False
    skill: str | None = None


PREFERENCE_RULES = [
    PreferenceRule("workflow", "architecture_first", "Prefers architecture-first setup before feature work", re.compile(r"architecture|foundation first|set up .* foundation|clean maintainable way|outside in", re.I), baseline=True, skill="liam-base"),
    PreferenceRule("workflow", "docs_first", "Prefers checking official docs for framework or library decisions", re.compile(r"official docs|best practices|documentation-first|docs first", re.I), baseline=True, skill="liam-base"),
    PreferenceRule("workflow", "anti_overengineering", "Prefers straightforward implementations and dislikes overengineering", re.compile(r"overengineer|overengineerd|straightforward|minimal implementations?|dont overengineer", re.I), baseline=True, skill="liam-base"),
    PreferenceRule("workflow", "atomic_commits", "Prefers atomic commits with small coherent changes", re.compile(r"atomic commit|alot of commits|commit hygiene|small focused changes", re.I), baseline=True, skill="commit-hygiene"),
    PreferenceRule("workflow", "tests_first", "Frequently asks for tests, linting, or explicit verification", re.compile(r"write tests|run tests|linting|ensure they pass|verify", re.I), baseline=True, skill="test-repair"),
    PreferenceRule("workflow", "current_state_cutover", "Prefers current-state cutovers over compatibility layers", re.compile(r"compatibility|fallback paths|current-state|cutover|legacy", re.I), baseline=True, skill="liam-base"),
    PreferenceRule("structure", "feature_based_structure", "Prefers feature-based structure with clear boundaries", re.compile(r"feature-based|modules architecture|clear boundaries|auth boundary|data[- ]access boundary", re.I), baseline=True, skill="liam-base"),
    PreferenceRule("structure", "thin_pages", "Prefers thin pages and route-local implementation details", re.compile(r"thin pages|route-local|keep pages.*thin|keep layouts.*thin", re.I), baseline=False, skill="liam-web-foundation"),
    PreferenceRule("workflow", "repo_reference", "Often references other repos before implementing", re.compile(r"another repo|other repo|sibling repo|reference repo|upstream", re.I), baseline=False, skill="repo-reference"),
    PreferenceRule("workflow", "design_directness", "Prefers direct design critique over vague praise", re.compile(r"be harsh|dont sugar coat|direct critique", re.I), baseline=False, skill="design-review"),
    PreferenceRule("product", "mobile_first", "Prefers mobile-first product and UI decisions", re.compile(r"mobile first", re.I), baseline=False, skill="liam-mobile-foundation"),
]


def build_stack_affinities(records: list[PromptRecord]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        for name, pattern in LIBRARY_PATTERNS.items():
            if pattern.search(record.text):
                counts[name] += 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _confidence_from_count(count: int) -> str:
    if count >= 8:
        return "high"
    if count >= 2:
        return "medium"
    return "low"


def build_preference_cards(records: list[PromptRecord]) -> list[PreferenceCard]:
    cards: list[PreferenceCard] = []
    for rule in PREFERENCE_RULES:
        matching = [record for record in records if rule.pattern.search(record.text)]
        if not matching:
            continue
        evidence: list[str] = []
        seen: set[str] = set()
        for record in matching:
            sample = record.text.strip().replace("\n", " ")
            if sample in seen:
                continue
            seen.add(sample)
            evidence.append(sample[:240])
            if len(evidence) == 3:
                break
        cards.append(
            PreferenceCard(
                category=rule.category,
                key=rule.key,
                label=rule.label,
                count=len(matching),
                confidence=_confidence_from_count(len(matching)),
                evidence=evidence,
            )
        )
    cards.sort(key=lambda card: (-card.count, card.label))
    return cards


def build_baseline_instructions(cards: list[PreferenceCard]) -> str:
    selected = [card for card in cards if card.confidence in {"high", "medium"}]
    if not selected:
        return "# Baseline Instructions\n\nNo strong repeated preferences were detected yet."

    lines = ["# Baseline Instructions", "", "Use these as the short always-on defaults inferred from repeated prompts:", ""]
    for card in selected[:8]:
        lines.append(f"- {card.label}")
    return "\n".join(lines) + "\n"


def build_candidate_skills(cards: list[PreferenceCard], stack_affinities: dict[str, int]) -> str:
    lines = ["# Candidate Skills", "", "These are suggested overlays inferred from repeated prompts.", ""]
    suggested: list[tuple[str, str]] = []

    strong = {card.key for card in cards if card.confidence in {"high", "medium"}}
    if strong & {"architecture_first", "docs_first", "anti_overengineering", "current_state_cutover", "feature_based_structure"}:
        suggested.append(("base-skill", "Durable baseline engineering preferences."))
    if stack_affinities.get("nextjs", 0) or stack_affinities.get("react", 0) or stack_affinities.get("drizzle", 0) or stack_affinities.get("better-auth", 0):
        suggested.append(("web-foundation", "Web stack defaults and structure preferences."))
    if stack_affinities.get("expo", 0) or stack_affinities.get("react-native", 0):
        suggested.append(("mobile-foundation", "Mobile structure and contract preferences."))
    if "repo_reference" in strong:
        suggested.append(("repo-reference", "Cross-repo exploration workflow."))
    if "atomic_commits" in strong:
        suggested.append(("commit-hygiene", "Atomic commit and diff-splitting preferences."))
    if "tests_first" in strong:
        suggested.append(("test-repair", "Test-first and expectation-audit workflow."))
    if "design_directness" in strong:
        suggested.append(("design-review", "Direct design critique and UI quality review."))

    if not suggested:
        lines.append("No strong skill candidates were inferred yet.")
        return "\n".join(lines) + "\n"

    for name, description in suggested:
        lines.append(f"## {name}")
        lines.append("")
        lines.append(description)
        lines.append("")
    return "\n".join(lines)


def build_working_style(cards: list[PreferenceCard], stack_affinities: dict[str, int]) -> str:
    lines = ["# Working Style", "", "This note is synthesized from repeated local prompt history.", ""]
    if cards:
        lines.append("## Strong repeated preferences")
        lines.append("")
        for card in cards[:10]:
            lines.append(f"- {card.label} ({card.confidence}, {card.count} matches)")
        lines.append("")
    if stack_affinities:
        lines.append("## Stack affinities")
        lines.append("")
        for name, count in list(stack_affinities.items())[:10]:
            lines.append(f"- {name}: {count}")
        lines.append("")
    return "\n".join(lines)
