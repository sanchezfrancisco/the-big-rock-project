# Architecture

Main flow:
1. Discovery: scan repository for `.py` files with ignore rules and secret redaction.
2. Chunking: parse AST and create contextual chunks (imports, docstrings, symbols).
3. Embedding: generate vectors with selected backend (`local` or `openai`).
4. Cache: persist embeddings by content hash and backend/model.
5. Store: save chunks and vectors to index SQLite.
6. Retrieval: hybrid score = vector similarity + keyword overlap.
7. Answering: produce summary plus citations.

Storage:
- Index DB: repository, file, chunk, query entities.
- Embedding cache DB: keyed vector cache to reduce reindex cost.
- Metrics log: `reports/metrics.jsonl`.

Key modules:
- `discovery.py`
- `chunking.py`
- `embeddings.py`
- `embedding_cache.py`
- `store.py`
- `qa.py`
- `eval.py`
- `api.py`
- `web/*`

