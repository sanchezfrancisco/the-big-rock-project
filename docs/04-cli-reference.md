# CLI Reference

Core commands:
- `scn index <repo>`
- `scn ask "<question>" [--top-k N]`
- `scn explain "<question>" [--top-k N]`
- `scn status`
- `scn reset-index`
- `scn doctor`

Evaluation:
- `scn eval <dataset.json> [--top-k N] [--report-out PATH] [--min-recall X]`
- `scn tune <dataset.json> [--top-k N] [--weights csv] [--report-out PATH]`

Cache:
- `scn cache-stats`
- `scn cache-prune --max-entries N`

Global options:
- `--index-path`
- `--json`

