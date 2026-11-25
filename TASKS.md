# Project task list

Work through one numbered task at a time. Each task is complete only when its acceptance criteria and verification are satisfied. Record evidence in the task entry; add follow-ups rather than concealing limitations. The current code is a prototype, not evidence that a task is complete.

Status: `[ ]` not started, `[~]` in progress, `[x]` complete, `[!]` blocked. Next task: **7**. The live pilot (Task 9) remains conditional on the open access and reuse decisions in the site inspection.

## Phase 1: Define the project

- [x] **1. Review the prototype.** Inspect code, tests, Git state, and documentation; identify defects, limitations, and what to retain. Run existing tests and record findings and follow-ups. Verification: five existing unit tests passed with `python3 -B -m unittest discover -s tests -v` on 2026-11-25; see [prototype review](PROTOTYPE_REVIEW.md) for findings and follow-ups.
- [x] **2. Define use case and scope.** Document intended users and questions, permitted hosts and content types, exclusions, and success criteria. Verification: reviewed [project scope](PROJECT_SCOPE.md) against the requested prospective and current student audiences; unresolved access, reuse, host, pilot, and evaluation decisions are recorded there.
- [x] **3. Establish development workflow.** Make setup, test commands, configuration, and the branch/PR workflow reproducible; add a GitHub Actions workflow that runs tests on pull requests. Verification: run setup and tests in a clean environment, validate the workflow configuration, and document results. Verify the actual GitHub run once a remote is available. Progress 2026-11-25: CI workflow added; five tests and CLI help pass on local Python 3.12. A `--without-pip` virtual environment ran all five tests successfully; normal venv creation lacks `ensurepip`. A clean copy in `/tmp` also passed all five tests and CLI help. GitHub repository created and initial push CI passed on Python 3.10 and 3.12 ([run](https://github.com/rehman-batt/fast-nuces-data-pipeline/actions/runs/45550635591)). PR-triggered CI passed on PR #1; main is protected with required PRs and Python checks. The CI action versions were updated in PR #2; both PR checks passed and the inspected job had no annotations. `actionlint` is not installed. A pip-enabled venv remains unverified locally, but a clean no-pip environment passed the tests.

## Phase 2: Discover and collect pages

- [x] **4. Inspect site structure and access rules.** Record current robots rules, relevant terms, redirects, content types, and unresolved permissions for each proposed host. Verification: cite checked URLs and dates; do not infer permission from missing evidence. Read-only HTTP checks and unresolved permission questions are recorded in [site inspection](SITE_INSPECTION.md); no live crawl was performed.
- [x] **5. Build URL discovery.** Discover links from approved starting pages and usable sitemaps. Verification: tests cover relative links, duplicate URLs, and unsupported schemes. Verification: nine local tests pass, including malformed URLs, duplicate links, sitemap parsing and host filtering. Sitemaps are optional URL sets; index and compressed sitemaps remain future work. The user reports FAST permission to use website data for a student chatbot; separate dataset redistribution is unconfirmed.
- [x] **6. Enforce crawl scope.** Apply host, path, and robots restrictions to initial URLs and redirects. Verification: ten local tests pass, including a synthetic crawl that checks external hosts, excluded and robots-disallowed paths, and a redirect to an excluded path. URL path interpretation can differ across servers; exclusions are defense in depth, not an access-control boundary.
- [ ] **7. Implement polite fetching.** Add appropriate timeouts, request pacing, bounded retries or backoff, size limits, and failure handling. Verification: deterministic tests simulate rate limits, server errors, timeouts, and oversized responses.
- [ ] **8. Save collection results.** Store successful responses and failure records with provenance; support safe repeated runs or resumption. Verification: tests cover persistence, failures, and repeat behavior; document retention and overwrite semantics.
- [ ] **9. Run a small live pilot.** Once rules and intended use have been checked, collect a bounded sample and inspect logs, coverage, and failures. Verification: record date, scope, counts, outcomes, and unresolved issues; do not claim a successful crawl without evidence.

## Phase 3: Extract and clean content

- [ ] **10. Extract HTML content.** Preserve useful headings, paragraphs, lists, and links while removing boilerplate. Verification: representative synthetic or permitted fixtures exercise extraction and regressions.
- [ ] **11. Extract tables.** Preserve row and column relationships for relevant pages. Verification: tests cover representative tables and manual comparison with sources.
- [ ] **12. Handle PDFs.** Extract permitted text-based PDFs with page-level provenance. Verification: tests cover representative PDFs and extraction failures; document treatment of scanned documents.
- [ ] **13. Normalize and validate documents.** Define and enforce a schema with source, collection time, content type, and relevant metadata. Verification: tests accept valid records and report malformed ones.
- [ ] **14. Remove duplicates.** Detect exact duplicates and assess whether near-duplicate detection is needed; preserve provenance. Verification: tests cover duplicates, distinct documents, and source retention.
- [ ] **15. Review content quality.** Compare a sample with source material and review privacy and reuse concerns. Verification: record sampling method, findings, and corrections or follow-ups.

## Phase 4: Prepare model-ready data

- [ ] **16. Chunk documents.** Preserve context and source references in bounded chunks. Verification: tests cover boundaries, overlap, short documents, and provenance.
- [ ] **17. Create an evaluation set.** Prepare reviewed questions with expected answers or supporting sources across relevant topics and campuses. Verification: inspect coverage and keep evaluation separate from training examples.
- [ ] **18. Build a retrieval baseline.** Return source-linked passages for queries. Verification: measure retrieval on the held-out evaluation set and report method, results, and failures.
- [ ] **19. Prepare fine-tuning examples.** If justified by the baseline, create reviewed, source-grounded examples and separate training and evaluation sets. Verification: inspect representative examples and document split methodology; otherwise record why this task is deferred.
- [ ] **20. Validate training data.** Check schema, duplicates, missing fields, and split leakage. Verification: automated checks and human review for accuracy and unsupported claims.

## Phase 5: Evaluate and present

- [ ] **21. Evaluate the assistant approach.** Compare retrieval-only with any fine-tuned approach using the same evaluation set. Verification: report method, evidence, limitations, and failure examples; if fine-tuning is deferred, report the baseline only.
- [ ] **22. Make runs reproducible.** Document configuration, commands, schemas, and dataset or run versions. Verification: reproduce a run in a clean environment within access constraints.
- [ ] **23. Polish the portfolio.** Present architecture, decisions, results, limitations, setup, and a concise demo. Verification: follow the README from a clean checkout and review all published content for rights and privacy.

## Git and GitHub workflow

The repository is connected to [GitHub](https://github.com/rehman-batt/fast-nuces-data-pipeline). For each task, inspect the working tree, create a focused branch, implement and test, and review the diff. Keep one task per branch and pull request where practical. GitHub Actions should run the test suite on each pull request once configured. After the user requests or authorizes commits, make a focused commit. Once a GitHub repository is selected or created with the user's authorization, configure it as a remote and use branches and pull requests for review. Never commit collected content or credentials without an explicit rights and privacy review.
