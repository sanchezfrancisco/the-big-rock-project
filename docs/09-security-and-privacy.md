# Security and Privacy

Defaults:
- Local-first embeddings (`local` backend).
- Secret redaction before indexing.
- Ignore controls with `.scnignore`.

OpenAI backend:
- Explicit opt-in via backend selection.
- Requires `OPENAI_API_KEY`.
- Recommended to restrict indexed paths to non-sensitive code where possible.

Operational recommendations:
- Keep index and cache files in protected local storage.
- Rotate API keys and avoid storing plaintext keys in repo files.

