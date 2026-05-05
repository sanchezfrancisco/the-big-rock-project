# Compatibility Matrix

## Runtime

| Component | Supported |
|---|---|
| Python | 3.11+ |
| OS | Windows, Linux, macOS (CLI/API/UI) |
| Storage | SQLite3 local files |

## Embedding Backends

| Backend | Status | Requirements | Notes |
|---|---|---|---|
| `local` | Stable | None | Deterministic hash embeddings, zero API cost. |
| `openai` | Stable (optional) | `pip install -e ".[providers]"`, `OPENAI_API_KEY` | Better semantic quality, external API cost. |

## Interfaces

| Interface | Status | Notes |
|---|---|---|
| CLI | Stable | Full operations including eval/tune/cache. |
| API | Stable | Runtime backend override per request supported. |
| Web UI | Stable | Includes index/ask/explain/eval/tune/cache/metrics. |

## CI

| Workflow | Status | Gate |
|---|---|---|
| `quality-eval` | Active | `recall@k` threshold via `scn eval --min-recall` |

