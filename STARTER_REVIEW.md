# Model-neutral starter review — 2026-11-25

A 12-example illustrative JSONL is stored locally as `data/training-v4.jsonl` (SHA-256 `4c7213d752c780c80bf449d0ceb23078b447128c444ba9e1f7a8cef30faeb6e8`). Its five selected source records are stored locally as `data/training-sources-v3.jsonl` (SHA-256 `4c9bbbbba8da77d447bf6e045de856079cce999e6d163fecaca962b716d4f21a`). Both remain Git-ignored; neither is a public dataset.

The examples use four training source URLs and one separate validation source URL. They include admissions, student financial-assistance and library questions. The `source_date` is the date the local source was observed, not a verified publication date. The validator found no exact question duplicates, train/validation source URL overlaps, or overlap with expected source URLs in the public development set. It found each evidence excerpt in the corresponding saved source text.

A same-author manual pass compared all 12 answers and evidence excerpts; five FAQ excerpts were expanded to include their question context. This is not independent expert review, and exact source matching does not prove an answer is correct or current. The university's pages may conflict or become stale; review and date-check them before use. People-list pages from the broader crawl were not used as sources for these examples.

This is an example of the format and validation workflow, not a training-ready corpus: there are only 11 training examples and one validation example. It cannot support a meaningful fine-tuning or generalization claim. More diverse, independently reviewed material, a separate unseen holdout, and an answer-quality baseline remain necessary. The user has not selected a model or platform; separately publishing source-derived data remains unconfirmed.
