# Prompt Profiler

Extract your own prompts from supported coding-agent harnesses, distill repeated preferences, and generate skill-ready outputs.

Prompt Profiler is for people who switch between agentic coding harnesses and do not want to keep repeating the same setup instructions, stack preferences, and workflow rules.

The extractor runs locally, reads supported prompt stores, normalizes your prompts into one schema, and emits:

- raw prompt archive
- cleaned prompt corpus
- deduped repeated prompts
- preference cards
- stack affinity summary
- candidate skill suggestions
- baseline instruction draft
- working-style note

It does not rely on transcript replay as the final product. The goal is a durable user operating profile.

## Supported Harnesses

High-confidence support in this repo:

- OpenCode
- Claude Code
- Codex
- Cursor
- Pi (Oh My Pi)

Not included in v1:

- OMP
- Continue
- Cline
- Roo Code
- OpenHands

Those may be added later through new handlers once their prompt stores are confirmed.

## Why this exists

A lot of agent users repeat the same things:

- set the architecture first
- do not overengineer
- use my preferred stack
- keep the structure maintainable
- prefer current canonical patterns
- make atomic commits
- verify the changed scope

This project turns those repeated instructions into structured outputs you can reuse as:

- a personal base skill
- stack-specific overlay skills
- a working-style document
- baseline project instructions

## Repository Layout

```text
skills/
└── prompt-profiler/
    ├── SKILL.md
    ├── references/
    └── scripts/
        ├── detect_harnesses.py
        ├── extract_preferences.py
        └── harness_preference_extractor/
tests/
```

The skill is self-contained under `skills/prompt-profiler/`.

## Quick Start

Clone the repo:

```bash
git clone https://github.com/liamvinberg/prompt-profiler.git
cd prompt-profiler
```

Detect which supported harnesses are present on the current machine:

```bash
python3 skills/prompt-profiler/scripts/detect_harnesses.py
```

Run the extractor locally and write outputs to `./output`:

```bash
python3 skills/prompt-profiler/scripts/extract_preferences.py --output-dir ./output
```

Limit extraction to specific harnesses:

```bash
python3 skills/prompt-profiler/scripts/extract_preferences.py \
  --harness opencode \
  --harness claude_code \
  --harness codex \
  --output-dir ./output
```

## Output Files

Typical outputs:

- `support_matrix.json`
- `raw_prompts.jsonl`
- `clean_prompts.jsonl`
- `deduped_prompts.jsonl`
- `preference_cards.jsonl`
- `stack_affinities.json`
- `candidate_skills.md`
- `baseline_instructions.md`
- `working_style.md`
- `summary.json`

## Installation as a Skill

Use the helper installer if you want to install into Claude Code, Codex, or Pi from the cloned repo:

```bash
python3 install.py claude
python3 install.py codex
python3 install.py pi
```

### Claude Code / OMC

Copy the skill folder into your Claude skills directory:

```bash
mkdir -p ~/.claude/skills
cp -R skills/prompt-profiler ~/.claude/skills/
```

Then either invoke it explicitly in your request or let the harness pick it up when the task matches.

Example opening request:

```text
Use the prompt-profiler skill to inspect my local agent harnesses, extract my own prompts, and generate a working-style profile.
```

### Codex

Copy the skill folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R skills/prompt-profiler ~/.codex/skills/
```

### Pi (Oh My Pi)

Copy the skill folder into your Pi skill directory:

```bash
mkdir -p ~/.pi/agent/skills
cp -R skills/prompt-profiler ~/.pi/agent/skills/
```

### OpenCode

OpenCode works better with a repo-level pack than a single loose skill folder. Clone this repository into the OpenCode skills root:

```bash
git clone https://github.com/liamvinberg/prompt-profiler.git \
  ~/.config/opencode/skills/prompt-profiler
```

The OpenCode-specific shape is already present under `skills/` in the repo.

## How the Skill Works

The skill follows a handler model.

Each supported harness has an adapter that knows how to:

- detect whether the harness is present
- list the supported local stores
- extract raw user-authored prompts
- normalize them into a shared schema

That keeps the system maintainable and makes it straightforward to add more harnesses later.

## Privacy Defaults

This project is local-only by default.

It does not need network access to extract or profile prompts.

Recommended usage:

- review outputs locally before sharing them
- treat prompt archives as sensitive data
- use the cleaned outputs for analysis rather than the raw archive when possible
- redact secrets or project names before publishing sample outputs

## Development

Run unit tests:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Run local extraction against the current machine:

```bash
python3 skills/prompt-profiler/scripts/extract_preferences.py --output-dir ./output
```

## Inspiration and Packaging Pattern

This repo intentionally follows the public patterns used by popular skill repositories:

- repo-level README with per-harness install guidance
- self-contained skill folder with `SKILL.md`
- optional `scripts/` and `references/` inside the skill
- explicit support matrix instead of vague compatibility claims

## License

MIT
