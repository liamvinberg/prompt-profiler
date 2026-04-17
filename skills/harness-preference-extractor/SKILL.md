---
name: harness-preference-extractor
description: Extract a user's own prompts from supported local coding-agent harnesses, normalize them into a shared schema, and distill repeated preferences into reusable outputs such as baseline instructions, working-style notes, and candidate custom skills. Use when a user wants to mine their own agent history across tools like OpenCode, Claude Code, Codex, Cursor, or Pi.
---

# Harness Preference Extractor

## Goal

Turn local prompt history into a durable user operating profile.

The main outputs should be:

- raw prompt archive
- cleaned prompt corpus
- repeated prompt clusters
- preference cards
- stack affinity summary
- baseline instruction draft
- candidate skill suggestions
- working-style note

## Start here

1. Run `scripts/detect_harnesses.py` first.
2. Show the supported harnesses detected on the machine.
3. Tell the user which harnesses are supported with high confidence.
4. Ask whether to extract all detected supported harnesses or only a subset.
5. Run `scripts/extract_preferences.py` with an explicit output directory.

## Supported harnesses in v1

- OpenCode
- Claude Code
- Codex
- Cursor
- Pi (Oh My Pi)

Do not assume support for other harnesses unless a handler exists and the local store was confirmed.

## Core rules

- Keep processing local-only by default.
- Prefer stable prompt stores over brittle cache or UI state files.
- Keep raw outputs for auditability.
- Use cleaned outputs for preference extraction.
- Distill stable repeated preferences rather than replaying full transcripts.
- Be explicit when a harness is present but unsupported.

## Output interpretation

When summarizing results:

- separate stable preferences from one-off requests
- separate stack preferences from workflow preferences
- separate baseline rules from candidate overlay skills
- say when confidence is low because evidence is sparse

## References

Read these when needed:

- `references/harness-matrix.md` for supported stores and caveats
- `references/output-schema.md` for the normalized record and output shapes
- `references/privacy-and-retention.md` for privacy defaults and redaction guidance
