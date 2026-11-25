# Initial retrieval baseline — 2026-11-25

A dependency-free, in-memory BM25 keyword ranker was evaluated on the initial 10-page pilot after exact-text deduplication: nine unique page texts produced 108 plain-text chunks. The pilot was collected before structured table extraction was added, so this run does not assess table-row chunks.

On the nine development questions whose expected sources were present in that pilot, the expected source URL appeared among the top five returned chunks for **8 of 9** cases. Three current-student questions were excluded because their expected source pages were not in the pilot. The calculator question missed: the query used a singular term while the source used the plural. Other matching terms produced results from unrelated admissions pages.

This is a source-level hit count, not passage relevance, answer accuracy, safety, or evidence that the system can answer correctly. Multiple chunks can come from one page; no manual passage-support scoring was performed. The question set is small, publicly visible and may guide development, so this is not an independent holdout benchmark or a generalization estimate. Scores will change with corpus snapshots, chunking and source changes. No language model or fine-tuning was evaluated.

To reproduce with the original local pilot data:

```bash
python3 -m fast_corpus.cli prepare --input data/pilot-retry-2026-11-25.jsonl --output data/pilot-chunks.jsonl
python3 -m fast_corpus.cli evaluate --input data/pilot-chunks.jsonl --questions evaluation/questions.jsonl --limit 5
```

The dataset itself is not committed; results cannot be reproduced without an equivalent authorized local snapshot. `prepare` replaces its output after successful validation. Check the snapshot date and expected-source coverage before interpreting the result.
