# Embedding Cache

Purpose:
- Reduce reindex time and API cost by reusing embeddings for unchanged text.

Cache key:
- `backend:model:dimensions:text_hash`

Persistence:
- SQLite file at `SCN_EMBEDDING_CACHE_PATH`.

Operations:
- Inspect: `scn cache-stats`
- Prune: `scn cache-prune --max-entries N`

Status fields:
- `embedding_cache_path`
- `embedding_cache_entries`
- `embedding_cache_hits`
- `embedding_cache_misses`

