# Reproducibility notes

Checked on 2026-11-25 using a clean local clone of `main` at commit `630c16a`. The project requires Python 3.10 or newer; the core pipeline uses the standard library. PDF tests require the optional `pypdf` dependency.

- System Python 3.12 ran 33 tests with three PDF tests skipped because `pypdf` was absent. The bundled Python with `pypdf` ran all 33. GitHub Actions installs `pypdf>=6,<7` and tests Python 3.10 and 3.12. That range is not an exact dependency lock; record the actual version used for any published result.
- In the clean clone, a synthetic source record prepared twice produced byte-identical chunks, and keyword search returned the expected synthetic passage. This verifies that small path only, not the full live collection or model behavior.
- The initial authorized pilot snapshot is local and Git-ignored. Its file `data/pilot-retry-2026-11-25.jsonl` had SHA-256 `6c3c1264ec952e32e19d152707f190931886117b9ae3f04f6254ce929bb7cc6b` when checked. The [baseline](evaluation/BASELINE.md) specifies the preparation and evaluation commands; a matching authorized snapshot is required to reproduce its number. A hash identifies the file, not its permission status or quality.
- Crawler output depends on site content, network responses, collection time, robots rules and configuration. Record the commit, dependency versions, run limits, host scope, timestamps and input hashes for each experiment. Do not commit the crawler contact, downloaded data, credentials or private material without appropriate review.

A clean clone and synthetic run do not establish that the complete future corpus or a model-training run is reproducible. Task 22 remains open until the full pipeline and its run metadata can be validated end to end.
