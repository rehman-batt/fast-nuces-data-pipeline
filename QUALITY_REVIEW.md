# Content quality review — 2026-11-25

## Sample and method

This is a targeted review, not a statistical estimate of corpus quality. From the 10-page pilot, we selected the admissions schedule and fee page because their tables affect time-sensitive answers. We compared the saved pilot text with newly fetched HTML and re-ran the current parser against the saved HTML samples. We also rendered the first page of the public admission-information prospectus PDF and compared its layout with extracted text. The current parser changes do not retroactively update the original pilot JSONL.

## Findings

- **HTML boilerplate:** Both original pilot records started with a Unicode BOM and breadcrumb text. The updated parser removes those elements in both inspected samples; headings and visible update text remain. Other layouts and boilerplate still need evaluation.
- **Tables:** The current table parser captured one schedule table and three fee tables in the inspected HTML. Spot checks matched the source cell order, including the schedule's merged graduate header and representative fee rows. This is not exhaustive table validation. Nested tables are unsupported, and the current preparation command does not yet turn structured tables into table-aware chunks (Task 16). Do not rely on current chunks for precise table answers.
- **PDF reading order:** The inspected admissions PDF is a three-column page. The text extractor produced text, but its order differs from the rendered page; non-empty extraction alone is not proof of correctness. Scanned or empty pages are flagged, not OCRed. PDF collection is currently a local import step.
- **Duplication:** The pilot homepage was collected at two URLs. Exact deduplication now retains both source records. Near-duplicate detection is deferred until a larger sample can be reviewed.
- **Privacy and rights:** An email-pattern scan of the 10 extracted pilot records found no email-like strings. This is not a personal-data audit; names, phone numbers, and other identifiers may still appear. The user reported permission to use university website data for the chatbot; permission to publish the dataset separately is unconfirmed. Collected data remains Git-ignored.

## Follow-up

Task 16 must produce table-aware chunks and test that headers and row values remain linked. Before answering student questions, build an evaluation set that checks actual source support, campus/year context, and stale or contradictory material. Review personal information and reuse rights before any broader release or dataset publication.
