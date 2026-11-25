# Initial local RAG store

The initial store is `data/rag-store-2026-11-25-v1.sqlite`, kept in the Git-ignored data directory. It was built on 2026-11-25 from `data/curated-eval-chunks-v2-2026-11-25.jsonl`, whose SHA-256 is `239cb1e18140ed89ef6ec9af5160cecb68c5a8879d6b92c50a32fc1eecef53d7`. Its metadata reports 371 indexed chunks, derived from 15 unique page texts in a filtered, 16-record snapshot.

The source snapshot combines the expanded main-site collection with selected student pages and excludes URLs containing `/campus/`. This is a small, targeted foundation, not a complete university corpus or a complete privacy review. It does not contain a verified current faculty directory or HOD information. The undergraduate rules landing page is indexed, but the scanned 2023 rules PDF remains unreviewed and is not in this store. Source publication dates and current applicability need separate verification.

The store uses SQLite FTS5 with Porter stemming for lexical retrieval; it contains no embeddings and does not generate answers. Each stored chunk carries source metadata from preparation. A local non-holdout search for library resources returned library-page results. This spot check is not an answer-quality or retrieval benchmark. Do not tune the retriever against the user-provided question set; obtain a new unseen set for future evaluation after any changes.

Inspect locally with:

```bash
python3 -m fast_corpus.cli store-info --store data/rag-store-2026-11-25-v1.sqlite
python3 -m fast_corpus.cli store-search --store data/rag-store-2026-11-25-v1.sqlite --query "library resources" --limit 3
```

The data store is local, may contain university content and contact information, and is not intended for public release without rights and privacy review. Fine-tuning is deferred while the RAG workflow is built and evaluated.
