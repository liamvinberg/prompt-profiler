# Privacy and Retention

## Defaults

- Run locally by default.
- Do not send extracted prompts to external services unless the user explicitly asks.
- Treat raw prompt archives as sensitive data.
- Prefer sharing cleaned summaries instead of raw archives.

## Recommended safeguards

- review raw outputs before publishing examples
- redact secrets, tokens, project names, or sensitive pasted content
- consider excluding anger or venting from cleaned outputs if the user wants a durable profile only
- keep output directories user-controlled and easy to delete

## Good practice

Preference extraction is most useful when it stores only stable repeated preferences, not every temporary session detail.

That means:

- keep short-lived preferences session-scoped when possible
- turn repeated preferences into compact cards
- retrieve those cards selectively rather than replaying transcripts
