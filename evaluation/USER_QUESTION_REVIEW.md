# User-written question retrieval check — 2026-11-25

## Method

The user supplied six questions independently of the public development question list. They were saved locally and were not used to tune the retriever before this check. The fixed in-memory BM25 retriever returned up to five chunks per question from the saved 371-chunk filtered snapshot. The run manifest records clean commit `e9f2555729f87cb3f25372dc5cc439a227bfdbf3`, snapshot hash `239cb1e18140ed89ef6ec9af5160cecb68c5a8879d6b92c50a32fc1eecef53d7`, and the local question-file hash. Questions, result passages and university data remain Git-ignored.

One same-author reviewer inspected returned passages. This is a small qualitative question-level check, not an independent expert review or a measurement of generated-answer accuracy. Some source documents overlap the development set or local training examples, and the questions are now known to the project; they are not an unseen final benchmark. No language model was called.

## Observations

| Topic | Retrieved evidence | Limitation or appropriate next step |
|---|---|---|
| Admission opening | No current admission schedule appeared in the top five. | The question needs an intake/year; the saved 2026 schedule is not evidence of a future opening. Ask for context or state that current dates are unavailable. |
| Named staff email | None of the top five passages identified the requested person. | Do not guess an address; find and verify an appropriate current official source. |
| Current department head | No top-five passage identified a department head. | The question lacks a campus and the index lacks a verified current source; ask for the campus and avoid guessing. |
| Semester fee | Relevant fee and FAQ passages appeared. | They describe dated, credit-based charges rather than one universal semester amount. Ask for program, credit load and intake, and verify current rules. |
| Scholarships | Relevant scholarship and assistance passages appeared. | The sources support a general availability answer, but eligibility, campus and current conditions need clarification. |
| BS AI test pattern | The test-pattern page appeared, but its flattened text labels a broader category rather than explicitly establishing the BS AI mapping. | Verify the program-specific mapping and current test cycle; do not infer it from the flattened table. |

The result shows source-coverage, freshness, ambiguity and table-context gaps. The retriever alone does not generate answers or implement clarification/abstention. A future assistant needs those behaviors, independently verified staff and program sources, and a separate unseen evaluation after any further tuning. Avoid treating source-level hits as proof of factual support.
