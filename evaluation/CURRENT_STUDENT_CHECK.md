# Current-student source coverage — 2026-11-25

The three student pages referenced in the development questions were fetched individually from `www.nu.edu.pk` with a two-second delay within each bounded run. The calendar and conduct pages had extractable text. The undergraduate-rules landing page produced only a short heading and link text; its HTML points to a 2023 undergraduate rules PDF on the separate `nu.edu.pk` host.

The apex host's `robots.txt` returned HTTP 404 when checked on 2026-11-25. The linked PDF was available over HTTPS and was downloaded locally under the user's reported FAST authorization. It is 14,888,226 bytes and 26 pages (SHA-256 `cddfe1f5e9770132e27d686abd1c2e6742ef4732f0c2f431ed514bc1691d2004`). Sampled pages 4, 6 and 11 produced no text with pypdf; a rendered page visibly contains text. The importer defaults to a 10 MB limit; optional bounded OCR is under test and requires Tesseract, which is not installed locally. OCR output is excluded from preparation until reviewed. The PDF was not indexed and its 2023 rules should not be assumed current without verification.

Combining those three landing-page records with the previous filtered local evaluation snapshot produced 16 records, 15 unique text hashes and 371 chunks. The local page snapshot SHA-256 is `cd96a27cb00c418e3050a608bc08000d6d530c4dcf4cc9c5ae026b2e9200d7d7`; the chunks hash is `239cb1e18140ed89ef6ec9af5160cecb68c9a8879d6b92c50a32fc1eecef53d7`. These files and the PDF remain Git-ignored. Removing `/campus/` paths is not a complete privacy audit.

With plural normalization and `--scope indexed`, the expected source URL appeared in the top five for 11 of 12 public development questions; `admissions-09` was the labeled-source miss. This count includes the undergraduate-rules landing page, not the PDF content. It is a source-level in-sample check, not proof of passage relevance, answer correctness, current rules, or performance on unseen questions. The corpus differs from earlier runs, so counts are not a controlled comparison.

```bash
python3 -m fast_corpus.cli evaluate --input data/curated-eval-chunks-v2-2026-11-25.jsonl --scope indexed --limit 5
```

`indexed` evaluates only questions with an expected source URL in the supplied index and reports excluded IDs. It does not verify whether a page contains useful evidence. The default `pilot` mode preserves the original pilot selection and fails if an expected pilot source is missing. Do not treat source presence as complete content coverage.
