# Harness Matrix

## Tier 1 support

### OpenCode
- store: `~/.local/share/opencode/opencode.db`
- format: SQLite
- extraction surface: `message` + `part`
- user filter: `message.data.role == user`
- note: OpenCode may expand attached file context into stored prompt text; the cleaner should strip obvious tool-expansion suffixes

### Claude Code
- store: `~/.claude/transcripts/*.jsonl`
- format: JSONL
- extraction surface: transcript lines with `type == user`

### Codex
- store: `~/.codex/history.jsonl`
- format: JSONL
- extraction surface: one JSON object per prompt entry
- note: this is cleaner than the rollout session files

### Cursor
- store: `~/.cursor/prompt_history.json`
- format: JSON array of strings
- extraction surface: each array item is a raw prompt string
- note: this source has low metadata but is simple and reliable

### Pi
- store: `~/.pi/agent/sessions/*/*.jsonl`
- format: JSONL
- extraction surface: entries with `type == message` and `message.role == user`

## Not in v1

These may be added later through confirmed handlers:

- Continue
- Cline
- Roo Code
- OpenHands

The main reason they are excluded is not lack of popularity. It is lack of a verified local prompt store in this project.
