# Retrieval passage review — 2026-11-25

## Method and limits

One reviewer inspected only the expected-source passages within the top five BM25 results for the nine pilot-covered development questions, using the original 10-page pilot snapshot and 108 text chunks. This is a same-author, subjective development review, not an independent benchmark. Other retrieved sources were not assessed for alternative support. No language model generated answers.

Labels: **supported** means at least one expected-source passage contains the requested core information; **partial** means useful information appears but key context or structure is incomplete; **missing** means no expected-source passage was retrieved. These labels do not establish that an answer would be accurate, current, complete, or safe.

| Case | Review | Reason |
|---|---|---|
| admissions-01 | Supported | A top passage describes the application submission method. |
| admissions-02 | Supported | A rank-five passage states the relevant awaiting-result condition. |
| admissions-03 | Supported | A rank-two passage lists engineering admission test options. |
| admissions-04 | Partial | The schedule appears, but the original text-only pilot flattened the table columns, making date-to-program mapping fragile. |
| admissions-05 | Supported | A top passage includes the negative-marking note. |
| admissions-06 | Missing | The expected test-pattern page was absent from the top five; singular/plural wording likely contributed. |
| admissions-07 | Partial | The fee page appears, but original table values are flattened and should not be mapped to programs without checking the source. |
| admissions-08 | Partial | The scholarship passage gives categories but cuts off additional continuation conditions. |
| admissions-09 | Supported | The prospectus page and section names appear, although linked PDF contents were not part of this pilot. |

On this narrow review, five cases had an expected-source passage with core support, three were partial and one lacked an expected-source passage. This is not a model-answer metric, and the small public question set cannot support a generalization claim. The three current-student questions were not reviewed because their expected sources were absent from the pilot index.

Structured table-row chunks have since been implemented, but the original pilot records predate table extraction. Recollect or re-extract appropriate sources and repeat a blinded passage review before claiming an improvement. Expand current-student coverage, create a separate unseen holdout, and evaluate generated answers against the source passages when a model is selected. Keep changing fees, dates and rules attributable to a dated source.
