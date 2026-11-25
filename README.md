# FAST-NUCES public web corpus

A small, dependency-free Python pipeline for collecting permitted public HTML pages and turning them into source-linked text chunks. It is a starting point for a university information assistant and a portfolio demonstration of responsible data engineering. **It does not train a model or provide a finished chatbot.**

## Try the offline demo

```bash
python3 -m fast_corpus.demo
```

This uses fictional example pages, creates temporary files, and retrieves a source-linked passage without network access or university data. It demonstrates retrieval only; it does not generate an answer.

## Pipeline

`allowed URLs → robots check → bounded crawl → JSONL pages → deduplicated source-linked chunks → local SQLite retrieval store`

The crawler follows links only on explicitly allowed hosts, checks `robots.txt` separately for each origin, limits request rate and page size, and stops on a rate limit or server error. Redirect targets are checked against the same scope and robots rules. If robots cannot be retrieved—including a missing file or a redirect—the crawler skips that origin by default. `--allow-missing-robots` explicitly permits an HTTP 404 only; 403, 429, 5xx, redirects and network failures still fail closed. A missing file is not a content license. This intentionally conservative choice can mean zero pages are collected. The crawler does not bypass logins or access controls.

## Requirements and quick start

Python 3.10 or newer; no third-party packages are needed for the basic pipeline. From the project directory:

```bash
python3 -m unittest discover -s tests -v
python3 -m fast_corpus.cli crawl --user-agent 'YourProjectBot/1.0 (contact: you@example.com)' --limit 30
python3 -m fast_corpus.cli prepare
```

Replace the contact information with your own. The crawl writes `data/pages.jsonl`; preparation writes `data/chunks.jsonl`. The crawl refuses to overwrite an existing output or companion `.log` file; choose a new output path for each run. The preparation command **overwrites** its output file. The `data/` directory is ignored by Git to avoid accidentally publishing collected content. Use `--help` on either command to see options. Run from the repository root, or install with `pip install -e .` and use the `fast-corpus` command.

The default allowlist is only `www.nu.edu.pk`. Explicitly add each host if needed, and review its rules first:

```bash
python3 -m fast_corpus.cli crawl --seed https://nu.edu.pk/ --host nu.edu.pk --user-agent 'YourProjectBot/1.0 (contact: you@example.com)' --limit 30
```

The seed's host must be included in the allowlist. Each hostname is exact; subdomains are not automatically included. The default delay is two seconds per origin, with a minimum of one second. The defaults also cap page fetch attempts at 100 and queued page URLs at 1,000; use `--max-attempts` and `--max-queued` to adjust them. Robots and explicitly provided sitemap requests are separate from the page-attempt limit. A 429 or 5xx stops the crawl rather than being retried. Query strings are retained, so use a small limit and inspect URLs before expanding scope. Repeat `--exclude-path /prefix` to exclude path prefixes; exclusions are defense in depth, not an access-control boundary, because server URL interpretation can differ.

## Records

Each page line includes `url`, `title`, `crawled_at` (UTC), `content_type`, `sha256` of extracted text, `text`, and `tables` (rows of cells including header, rowspan and colspan). Each chunk includes a stable content-derived ID, source URL and title, source timestamp and its kind (`crawled_at` or `processed_at`), content type, optional PDF page number, and text. Input records are validated and a prior output is replaced only after all input records are valid. Identical extracted text is deduplicated, with all distinct source records retained in each chunk’s `sources` list. Near-duplicates are not merged. Text chunks overlap by 150 characters by default. Structured tables also produce `table_row` chunks with headers and source records. A table row longer than the configured chunk size stops preparation without replacing prior output; nested tables remain unsupported. The crawl timestamp is **not** the page's publication or update date.

## Responsible use and limitations

- Check each host's current robots rules, terms, copyright and permission for your intended collection, training and publication. A public page is not necessarily licensed for model training or redistribution. Review personal information before use.
- This is an HTML pilot, not a complete site mirror. The crawler does not download PDFs, OCR images, or render JavaScript; it also cannot parse sitemap indexes or compressed sitemaps, or extract nested tables. Page records include structured tables. Preparation adds table-row chunks with header context while retaining ordinary text chunks; those ordinary chunks may still contain flattened table text, so retrieval evaluation must check source support. Optional `--sitemap` arguments support XML URL sets subject to host and robots checks. Its simple HTML parser can retain boilerplate or miss content. The page limit counts successfully extracted pages, not all attempted URLs.
- Check sample pages and chunks against their sources. Verify current fees, dates, campus applicability, and conflicting or stale information with the university. Each crawl writes a companion log with skipped pages and failures. Logs can include URLs and should be reviewed before sharing. Interrupted runs can leave partial output and are not automatically resumable.
- The pipeline extracts text rather than preserving raw HTML. Exact-text hashes do not detect near-duplicates, and character-based chunks can split context. These limitations should be addressed before production use.
- Avoid committing collected text until you have reviewed rights and privacy implications. Examples and tests in this repository use synthetic data.

## From corpus to assistant

1. Inspect and clean collected content. Review PDF pages and table-aware chunks before using them.
2. Index chunks with keyword and semantic retrieval; retain source links and dates in answers.
3. Create a held-out question set across admissions, fees and campus policies. Measure retrieval quality and whether answers are supported by sources.
4. If needed, create **reviewed** question-answer examples and compare fine-tuning plus retrieval against a retrieval-only baseline. Raw pages or these chunks are not ready-made supervised fine-tuning examples.

A portfolio write-up should report the crawl date, scope, observed coverage, limitations and evaluation results. Do not claim measurements or model performance until you have actually run and evaluated the pipeline.

## Project management and version control

The ordered roadmap and acceptance criteria are in [TASKS.md](TASKS.md). Agent-specific working instructions are in [AGENTS.md](AGENTS.md). We intend to complete and review one task at a time, with tests and documented results.

This directory is a local Git repository. The GitHub remote is [rehman-batt/fast-nuces-data-pipeline](https://github.com/rehman-batt/fast-nuces-data-pipeline). Changes use focused branches, reviewable commits and pull requests into protected `main`. Check `git status` and review changes before committing; keep collected data and credentials out of version control. The pipeline remains a prototype; see the task tracker for completed work and open evaluation and data-review tasks.

## Engineering practices

- Keep changes focused, with one task per branch and pull request where practical. Run relevant checks and review the diff before merging.
- Maintain meaningful automated tests. A GitHub Actions workflow is configured to run the test suite on pull requests; its first push run passed on Python 3.10 and 3.12. Pull-request checks have also passed.
- Document setup, dependencies, configuration, commands, and run or dataset versions so results can be reproduced.
- Preserve source provenance and document access and reuse decisions. Do not commit credentials, personal data, or unreviewed collected content.
- Evaluate extraction and retrieval on a documented sample, reporting the methods, actual results, and limitations.

The core pipeline has no third-party runtime dependencies; PDF extraction requires the optional `pypdf` package, and OCR also requires external tools. For an isolated environment, install your operating system’s Python virtual-environment support and run `python3 -m venv .venv`; on the development machine, `ensurepip` was unavailable on 2026-11-25, so a pip-enabled environment has not yet been verified there. The tests also pass in an isolated `python3 -m venv --without-pip .venv` environment.

## Local PDF extraction

For an authorized PDF saved locally, install the optional dependency with `pip install -e '.[pdf]'`, then run:

```bash
python3 -m fast_corpus.cli extract-pdf --input path/to/document.pdf --source-url https://www.nu.edu.pk/example.pdf --output data/pdf-pages.jsonl
```

This command does not download PDFs or verify that the supplied source URL corresponds to the local file. It refuses to overwrite output and writes one record per page with `url`, one-based `page`, `processed_at`, text, a text hash, and `needs_ocr_review` for empty pages. Processing time is not the original crawl time. Use `--ocr` to attempt OCR only on pages without native text; this requires `pdftoppm` and `tesseract` on PATH. A local rules-PDF spot check is documented in [OCR_CHECK.md](OCR_CHECK.md); its output remains unreviewed. OCR output is flagged `needs_ocr_review` and excluded from preparation and source-evidence validation until a human verifies and explicitly clears that flag. If text is corrected, recompute its SHA-256 before preparation. Non-empty extraction does not guarantee correct text or reading order: inspect layouts and columns before use. The default PDF input limit is 10,000,000 bytes and 100 pages; `--max-bytes` and `--max-pages` explicitly adjust them. PDF page records can be passed to `prepare`; its chunks retain the PDF page number and distinguish processing time from crawl time.

## Persistent RAG data store

Build a local SQLite full-text store from prepared chunks, then inspect and query it:

```bash
python3 -m fast_corpus.cli store-build --input data/chunks.jsonl --output data/rag-store.sqlite
python3 -m fast_corpus.cli store-info --store data/rag-store.sqlite
python3 -m fast_corpus.cli store-search --store data/rag-store.sqlite --query "library resources" --limit 5
```

This requires SQLite with FTS5. Each result retains its source URLs, source timestamp and kind, content type, and optional PDF page number. The store metadata records the input JSONL SHA-256 and chunk count. It validates chunk structure, rejects explicitly flagged unreviewed OCR, and builds a new snapshot before publishing it. Existing stores are protected by default; pass `--replace` only when deliberately rebuilding, in which case validation must succeed before the old store is replaced. Keep the database in the Git-ignored `data/` directory and review its contents before any sharing.

This is a **lexical retrieval store**, using SQLite FTS5 with English Porter stemming. It is not a vector/embedding index, does not verify the truth or freshness of source text, and does not generate answers. It expects chunks created by the preparation pipeline; structural validation cannot detect a missing or falsified review flag. RAG answer generation, an appropriate model and any semantic index remain future work.

## Search baseline

Prepare a local collection and run `python3 -m fast_corpus.cli search --input data/chunks.jsonl --query "How do I apply?"`. The in-memory BM25 baseline applies a simple English trailing-`s` normalization and returns matching chunks and source metadata; it does not generate answers. Run `python3 -m fast_corpus.cli evaluate --input data/chunks.jsonl` to score pilot-covered development questions. Add `--scope indexed` to score cases whose labeled sources are in a different index; the output lists excluded cases and does not verify evidence support. The initial result and its limitations are documented in [evaluation/BASELINE.md](evaluation/BASELINE.md).

For reproducible local experiments, the `manifest` command records input hashes, selected non-secret settings and environment metadata. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for its limitations.
