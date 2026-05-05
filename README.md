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
scn eval eval/eval_dataset.real.json
scn eval eval/eval_dataset.real.json --report-out reports/eval.json --min-recall 0.20
scn tune eval/eval_dataset.real.json --weights 0.20,0.35,0.55,0.70 --report-out reports/tune.json
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
- Embeddings are cached locally in `.scn/embeddings_cache.sqlite3` to reduce reindex cost/latency.
- Optional `.scnignore` patterns can exclude sensitive or noisy paths.

## Commands

- `scn index <repo>`: build or rebuild the local index.
- `scn ask <question>`: retrieve relevant chunks and produce an evidence-first answer.
- `scn explain <question>`: inspect ranking scores (hybrid, vector, keyword).
- `scn status`: show index health and repository stats.
- `scn reset-index`: delete the local index.
- `scn doctor`: check runtime and SQLite health.
- `scn eval <dataset.json>`: run recall and latency metrics against an eval set.
- `scn eval ... --report-out reports/eval.json --min-recall 0.40`: export report and fail under quality gate.
- `scn tune ... --weights ... --report-out reports/tune.json`: pick the best hybrid keyword weight.

## Production Quality Loop

- Build index: `scn index <repo>`
- Run eval: `scn eval <dataset> --report-out reports/eval.json --min-recall <target>`
- Inspect ranking: `scn explain "<query>" --top-k 5`
- Track report artifacts under `reports/` for trend analysis.

## Optional Provider Embeddings

- Keep default: `SCN_EMBEDDING_BACKEND=local`
- Use external provider: set `SCN_EMBEDDING_BACKEND=openai`, `OPENAI_API_KEY`, and install provider deps:
  - `pip install -e ".[providers]"`

## Agile Learning System

The project is intentionally scoped for 6-8 hours/week:

- WIP limit: 2 active learning tasks.
- 20% weekly buffer for blockers or deeper practice.
- If a concept blocks progress for more than 3 days, treat it as a black box, ship the slice, and revisit it during buffer time.
