# Scanned rules OCR check — 2026-11-25

After the user installed Tesseract 5.3.4, the optional OCR path processed the locally retained 26-page undergraduate rules PDF. The input SHA-256 is `cddfe1f5e9770132e27d686abd1c2e6742ef4732f0c2f431ed514bc1691d2004`. The output file is local and Git-ignored; its SHA-256 is `57b3f1964a0f0a073096c2cbcb419f2e2eaf1386d6161c130c39a0b8b967ccc7`.

The run returned 26 page records: 24 used OCR and are flagged for review, and two had non-empty native text. One OCR page was empty. The flag prevents unreviewed OCR pages from entering prepared chunks or passing source-evidence validation. Native text also requires quality review: one native page contained a replacement/null character and contact-like content, demonstrating that non-empty text does not guarantee quality or privacy.

A visual spot check compared pages 4 and 6 with their extracted text. Page 6's opening was readable; page 4's table of contents contained repeated characters and a spelling error. This is not a full-page or full-document accuracy audit. No pages were marked reviewed or added to the retrieval index. The document is labeled 2023; its present applicability is unverified.

A separate synthetic image-only PDF was used to test Tesseract locally and is suitable for CI without uploading university data. The OCR workflow depends on `pypdf`, `pdftoppm`, and `tesseract`; limits and failure behavior are documented in the README. Human review, correction, privacy checks, and date verification remain necessary before using the extracted rules.
