# API Reference

Endpoints:
- `GET /health`
- `GET /`
- `POST /index`
- `POST /ask`
- `POST /explain`
- `GET /status`
- `POST /eval`
- `POST /tune`
- `GET /cache/stats`
- `POST /cache/prune`
- `GET /metrics/recent`
- `GET /suggest`

Runtime override fields (where supported):
- `embedding_backend`
- `hybrid_keyword_weight`
- `embedding_cache_path`

Notes:
- API supports request-level backend selection from UI.
- `/suggest` powers dynamic question suggestions and tab-complete behavior.

