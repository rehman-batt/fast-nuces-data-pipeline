# Table-aware retrieval check — 2026-11-25

The newer preparation pipeline was run against a local filtered snapshot: the 25-record expanded collection excluding URLs whose path contains `/campus/` (case-insensitive), plus the separately collected student financial-rules and library pages. This produced 13 source records, 12 unique text hashes and 344 chunks. The pages contained 22 extracted tables. Excluding those paths is a narrow relevance filter, not a complete personal-data or rights review.

The exact local input `data/curated-eval-pages-2026-11-25.jsonl` has SHA-256 `e2ed34c768abf1046a4b3cb55f5d4642dad1c69ccf3013800ea660f8beec831d`. The prepared chunks `data/curated-eval-chunks-2026-11-25.jsonl` have SHA-256 `4b4deea047972d66dd3b02ee37b9d2474f04e42c2b9d4480734a314fd299ebb3`. They remain Git-ignored. The run used the repository at commit `0de58b4`, default chunk size and overlap, and BM25 top five.

For the same nine `in_corpus` development cases used in the pilot baseline, the expected URL appeared in the top five for **6 of 9**. The expected URLs were absent for `admissions-03`, `admissions-06`, and `admissions-09`. The three current-student cases remained excluded because their labeled sources were not in this index. A missed labeled URL is not proof that no other retrieved source can answer the question. The score does not assess passage support or model answers.

This result is not a controlled comparison to the earlier 8/9: both the source snapshot and chunk representation changed, and the development set is very small and public. A manual, preferably independent, passage review and a separate unseen holdout are still needed. Ordinary text chunks may still contain flattened table text even though table-row chunks now exist. No model has been trained or evaluated.

To rerun on the saved local snapshot:

```bash
python3 -m fast_corpus.cli prepare --input data/curated-eval-pages-2026-11-25.jsonl --output data/curated-eval-chunks-retry.jsonl
python3 -m fast_corpus.cli evaluate --input data/curated-eval-chunks-retry.jsonl --questions evaluation/questions.jsonl --limit 5
```

## Development iteration: simple plural normalization

On the exact same saved 344-chunk snapshot and nine public development questions, a deliberately simple trailing-`s` normalization changed the expected-source top-five count from 6/9 to 8/9; `admissions-09` remained a labeled-source miss. The test-pattern page appeared at rank three for the calculator question and contained the relevant note. This change was motivated partly by a failure observed in this development set, so the result is in-sample and is not an independent estimate of improvement. The heuristic is not a full stemmer and can conflate distinct words; use a separate unseen holdout and passage/answer review before drawing conclusions.
