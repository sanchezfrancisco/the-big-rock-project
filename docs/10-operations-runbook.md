# Operations Runbook

Daily flow:
1. `scn doctor`
2. `scn index <repo>`
3. `scn ask ...` / `scn explain ...`
4. `scn eval ... --report-out ... --min-recall ...`

Weekly flow:
1. `scn tune ... --report-out ...`
2. Adjust `SCN_HYBRID_KEYWORD_WEIGHT` from tuning results.
3. Prune cache if needed.

Cache maintenance:
- `scn cache-stats`
- `scn cache-prune --max-entries 5000`

UI operations:
- Start API: `uvicorn semantic_code_navigator.api:app --reload`
- Use runtime panel to switch backend and parameters.

