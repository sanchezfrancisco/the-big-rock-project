# Configuration

Environment variables:
- `SCN_INDEX_PATH` default `.scn/index.sqlite3`
- `SCN_EMBEDDING_CACHE_PATH` default `.scn/embeddings_cache.sqlite3`
- `SCN_MAX_FILE_BYTES` default `512000`
- `SCN_VECTOR_DIMENSIONS` default `256`
- `SCN_DEFAULT_TOP_K` default `5`
- `SCN_EMBEDDING_BACKEND` default `local` (`local` or `openai`)
- `SCN_HYBRID_KEYWORD_WEIGHT` default `0.35` range `[0,1]`
- `SCN_OPENAI_EMBED_MODEL` default `text-embedding-3-small`
- `OPENAI_API_KEY` required for backend `openai`

Repository controls:
- `.scnignore` supports path patterns to exclude files/folders from indexing.

