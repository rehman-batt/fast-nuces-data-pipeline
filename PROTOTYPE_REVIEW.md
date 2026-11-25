# Prototype review — 2026-11-25

## Baseline

The repository has no commits or GitHub remote. All project files are currently untracked. The existing prototype provides a standard-library command-line crawler, HTML text extraction, JSONL output, exact deduplication and character-based chunks. It restricts hosts, checks robots per origin, spaces requests, caps response size and fails closed when robots cannot be retrieved. These are useful starting points to retain and validate, not production guarantees.

Verification: `python3 -B -m unittest discover -s tests -v` passed all five existing tests on 2026-11-25. They use synthetic inputs and do not demonstrate live-site coverage or compliance. No live crawl was performed during this review.

## Findings and follow-ups

- **Discovery can fail on malformed URLs.** `normalize` accesses `parts.port`, which can raise `ValueError` on an invalid port; a bad link can terminate a crawl. Address and test malformed inputs in Task 5.
- **The page limit does not bound attempts.** It counts successfully extracted pages, so a site with many non-HTML or failing links can generate substantially more requests. Add explicit attempt and queue limits in Tasks 5–7.
- **Collection is not resumable or auditable enough.** Output is overwritten; errors only appear in logs, and raw responses are not retained. Define persistence, retention and failure records in Task 8.
- **Redirects and robots need broader tests.** Current tests cover only robots retrieval failure and basic host checks; no end-to-end tests verify redirect restrictions, pacing, response limits or errors. Address in Tasks 6–7.
- **Extraction is simplistic.** HTML parsing can include boilerplate, join table cells, and lose document structure; PDFs and JavaScript-rendered content are unsupported. Address scope and representative fixtures in Tasks 10–12.
- **Deduplication drops alternate sources.** Only the first URL for duplicate text survives, so provenance is incomplete. Address in Task 14.
- **Chunking and input validation need stronger checks.** Character splits can break context; malformed JSON or missing fields can interrupt preparation, potentially after overwriting output. Address schema and safe output handling in Tasks 8, 13 and 16.
- **No evaluation or model training exists.** The current pipeline cannot establish answer quality or fine-tuning value. Address through Tasks 17–21.

## Git status and next step

The existing `master` branch is unborn, so task branches and PRs cannot yet start from a committed `main`. Establish an initial baseline and connect GitHub when authorized and available; do not claim a PR exists. Next: Task 2, define the use case and scope. The user identified both prospective and current students as the intended initial audience.
