# Semantic Code Navigator

Local-first CLI + API for indexing private Python repositories and asking technical questions with verifiable file/line citations.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
scn index C:\path\to\python\repo
scn ask "Where is user authentication handled?"
scn explain "how ranking was computed for auth?"
scn status
scn eval eval/eval_dataset.sample.json
```

Run the local API:

```powershell
uvicorn semantic_code_navigator.api:app --reload
```
Open `http://127.0.0.1:8000` for the local web UI.

## Privacy Defaults

- Embeddings are generated locally with a deterministic hashing model.
- Code is not sent to external AI providers.
- Common secrets are detected and redacted before indexing.
- The index is stored locally in `.scn/index.sqlite3` by default.
- Optional `.scnignore` patterns can exclude sensitive or noisy paths.

## Commands

- `scn index <repo>`: build or rebuild the local index.
- `scn ask <question>`: retrieve relevant chunks and produce an evidence-first answer.
- `scn explain <question>`: inspect ranking scores (hybrid, vector, keyword).
- `scn status`: show index health and repository stats.
- `scn reset-index`: delete the local index.
- `scn doctor`: check runtime and SQLite health.
- `scn eval <dataset.json>`: run recall and latency metrics against an eval set.

## Agile Learning System

The project is intentionally scoped for 6-8 hours/week:

- WIP limit: 2 active learning tasks.
- 20% weekly buffer for blockers or deeper practice.
- If a concept blocks progress for more than 3 days, treat it as a black box, ship the slice, and revisit it during buffer time.
