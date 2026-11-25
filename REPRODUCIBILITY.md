# Reproducibility notes

Checked on 2026-11-25 using a clean local clone of `main` at commit `630c16a`. The project requires Python 3.10 or newer; the core pipeline uses the standard library. PDF tests require the optional `pypdf` dependency.

- System Python 3.12 ran 33 tests with three PDF tests skipped because `pypdf` was absent. The bundled Python with `pypdf` ran all 33. GitHub Actions installs `pypdf>=6,<7` and tests Python 3.10 and 3.12. That range is not an exact dependency lock; record the actual version used for any published result.
- In the clean clone, a synthetic source record prepared twice produced byte-identical chunks, and keyword search returned the expected synthetic passage. This verifies that small path only, not the full live collection or model behavior.
- The initial authorized pilot snapshot is local and Git-ignored. Its file `data/pilot-retry-2026-11-25.jsonl` had SHA-256 `6c3c1264ec952e32e19d152707f190931886117b9ae3f04f6254ce929bb7cc6b` when checked. The [baseline](evaluation/BASELINE.md) specifies the preparation and evaluation commands; a matching authorized snapshot is required to reproduce its number. A hash identifies the file, not its permission status or quality.
- Crawler output depends on site content, network responses, collection time, robots rules and configuration. Record the commit, dependency versions, run limits, host scope, timestamps and input hashes for each experiment. Do not commit the crawler contact, downloaded data, credentials or private material without appropriate review.

A clean clone and synthetic run do not establish that the complete future corpus or a model-training run is reproducible. Task 22 remains open until the full pipeline and its run metadata can be validated end to end.

## Run manifests

Use `python3 -m fast_corpus.cli manifest --input data/pages.jsonl --input data/chunks.jsonl --setting chunk_size=1200 --setting overlap=150 --output data/run-manifest.json` to record input basenames, sizes and SHA-256 hashes, explicit settings, Python/pypdf versions, timestamp, and the Git state of the current working directory. The manifest never overwrites an existing file. Use only non-secret settings; filenames and settings may themselves be sensitive. The Git status records tracked and untracked changes but ignores Git-ignored files. If the tree is dirty, a commit hash alone does not reproduce the run.

Create the manifest at the time of the run; a later manifest does not prove which code or settings produced an earlier artifact. Hashes identify exact files but do not establish permission or correctness. Manifests are metadata only and do not include data or install dependencies. Full corpus and model-run reproducibility remains open.

## Later clean-checkout check

On 2026-11-25, a clean local clone at commit `71df507` ran all 48 tests with the bundled Python and PDF dependency, with Tesseract installed, and the offline synthetic demo returned its expected fictional source. This does not reproduce university collection or any model training. The local OCR output remains unreviewed.
