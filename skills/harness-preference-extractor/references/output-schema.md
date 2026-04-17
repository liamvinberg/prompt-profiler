# Output Schema

## Normalized prompt record

```json
{
  "harness": "opencode",
  "store": "~/.local/share/opencode/opencode.db",
  "session_id": "ses_...",
  "timestamp": "2026-04-17T11:00:00Z",
  "cwd": "/path/to/project",
  "source_path": "/absolute/path/to/store",
  "text": "raw user-authored prompt",
  "normalized_text": "dedupe-friendly text",
  "flags": ["system_like", "housekeeping", "anger"],
  "include_cleaned": true
}
```

## Output files

### `support_matrix.json`
Detected harnesses, stores, support confidence, and extraction notes.

### `raw_prompts.jsonl`
Every extracted prompt record before preference filtering.

### `clean_prompts.jsonl`
Prompt records suitable for preference analysis after excluding low-signal items.

### `deduped_prompts.jsonl`
Repeated prompts grouped by normalized text.

### `preference_cards.jsonl`
Structured preference signals with counts, confidence, category, and evidence.

### `stack_affinities.json`
Count summary for recognized stack/library mentions.

### `baseline_instructions.md`
Short always-on instruction draft based on the strongest stable preferences.

### `candidate_skills.md`
Suggested custom skill overlays inferred from repeated user patterns.

### `working_style.md`
Human-readable note describing the inferred working style.

### `summary.json`
Counts, top repeated prompts, top preferences, and generation metadata.
