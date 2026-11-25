# FAST-NUCES public web corpus

A small, dependency-free Python pipeline for collecting permitted public HTML pages and turning them into source-linked text chunks. It is a starting point for a university information assistant and a portfolio demonstration of responsible data engineering. **It does not train a model or provide a finished chatbot.**

## Pipeline

`allowed URLs → robots check → bounded crawl → JSONL pages → exact deduplication → source-linked JSONL chunks`

The crawler follows links only on explicitly allowed hosts, checks `robots.txt` separately for each origin, limits request rate and page size, and stops on a rate limit or server error. Redirect targets are checked against the same scope and robots rules. If robots cannot be retrieved—including a missing file or a redirect—the crawler skips that origin. This intentionally conservative choice can mean zero pages are collected. The crawler does not bypass logins or access controls.

## Requirements and quick start

Python 3.10 or newer; no third-party packages are needed for the basic pipeline. From the project directory:

```bash
python3 -m unittest discover -s tests -v
python3 -m fast_corpus.cli crawl --user-agent 'YourProjectBot/1.0 (contact: you@example.com)' --limit 30
python3 -m fast_corpus.cli prepare
```

Replace the contact information with your own. The crawl writes `data/pages.jsonl`; preparation writes `data/chunks.jsonl`. Both commands **overwrite** their output files. The `data/` directory is ignored by Git to avoid accidentally publishing collected content. Use `--help` on either command to see options. Run from the repository root, or install with `pip install -e .` and use the `fast-corpus` command.

The default allowlist is only `www.nu.edu.pk`. Explicitly add each host if needed, and review its rules first:

```bash
python3 -m fast_corpus.cli crawl --seed https://nu.edu.pk/ --host nu.edu.pk --user-agent 'YourProjectBot/1.0 (contact: you@example.com)' --limit 30
```

The seed's host must be included in the allowlist. Each hostname is exact; subdomains are not automatically included. The default delay is two seconds per origin, with a minimum of one second. Query strings are retained, so use a small limit and inspect URLs before expanding scope.

## Records

Each page line includes `url`, `title`, `crawled_at` (UTC), `content_type`, `sha256` of extracted text, and `text`. Each chunk includes a stable content-derived ID, its source URL and title, crawl time, and text. Identical extracted pages are deduplicated; the first source is retained. Chunks overlap by 150 characters by default. The crawl timestamp is **not** the page's publication or update date.

## Responsible use and limitations

- Check each host's current robots rules, terms, copyright and permission for your intended collection, training and publication. A public page is not necessarily licensed for model training or redistribution. Review personal information before use.
- This is an HTML pilot, not a complete site mirror. It does not extract PDFs, OCR images, render JavaScript, parse sitemaps, or extract tables as structured data. Its simple HTML parser can retain boilerplate or miss content. The page limit counts successfully extracted pages, not all attempted URLs.
- Check sample pages and chunks against their sources. Verify current fees, dates, campus applicability, and conflicting or stale information with the university. The crawler's logs report skipped pages and failures; save them if you need an audit trail.
- The pipeline extracts text rather than preserving raw HTML. Exact-text hashes do not detect near-duplicates, and character-based chunks can split context. These limitations should be addressed before production use.
- Avoid committing collected text until you have reviewed rights and privacy implications. Examples and tests in this repository use synthetic data.

## From corpus to assistant

1. Inspect and clean a small crawl. Add PDF extraction and structured tables only where needed and permitted.
2. Index chunks with keyword and semantic retrieval; retain source links and dates in answers.
3. Create a held-out question set across admissions, fees and campus policies. Measure retrieval quality and whether answers are supported by sources.
4. If needed, create **reviewed** question-answer examples and compare fine-tuning plus retrieval against a retrieval-only baseline. Raw pages or these chunks are not ready-made supervised fine-tuning examples.

A portfolio write-up should report the crawl date, scope, observed coverage, limitations and evaluation results. Do not claim measurements or model performance until you have actually run and evaluated the pipeline.

## Project management and version control

The ordered roadmap and acceptance criteria are in [TASKS.md](TASKS.md). Agent-specific working instructions are in [AGENTS.md](AGENTS.md). We intend to complete and review one task at a time, with tests and documented results.

This directory is a local Git repository. No GitHub remote is currently configured. The intended workflow is a focused branch and reviewable commit for each task, followed by a pull request once a GitHub repository is connected. Check `git status` and review changes before committing; keep collected data and credentials out of version control. The existing code is a prototype and is scheduled for review in Task 1.

## Engineering practices

- Keep changes focused, with one task per branch and pull request where practical. Run relevant checks and review the diff before merging.
- Maintain meaningful automated tests. A GitHub Actions workflow is configured to run the test suite on pull requests; its first live run is pending a connected GitHub repository.
- Document setup, dependencies, configuration, commands, and run or dataset versions so results can be reproduced.
- Preserve source provenance and document access and reuse decisions. Do not commit credentials, personal data, or unreviewed collected content.
- Evaluate extraction and retrieval on a documented sample, reporting the methods, actual results, and limitations.

The project currently has no runtime dependencies. For an isolated environment, install your operating system’s Python virtual-environment support and run `python3 -m venv .venv`; on the development machine, `ensurepip` was unavailable on 2026-11-25, so a pip-enabled environment has not yet been verified there. The tests also pass in an isolated `python3 -m venv --without-pip .venv` environment.
