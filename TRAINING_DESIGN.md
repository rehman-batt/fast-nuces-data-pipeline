# Fine-tuning data design

Status: planning, not a training-ready dataset. The initial pilot contained 10 pages and a later run collected 25; retrieval has only a small source-level development score, and no model answer quality has been evaluated. The user has not yet selected a model or platform; work is proceeding in a model-neutral format.

## Proposed model-neutral record

Each reviewed training example should include an instruction or user question, the desired assistant response, a source URL, the source passage or a stable passage identifier, the source date or collection version, and any campus, program or academic-year context needed to interpret the answer. The current neutral JSONL format uses `question`, `answer`, `evidence`, `source_url`, `source_date` (YYYY-MM-DD) and `split` (`train` or `validation`). Final serialization must follow the selected model or platform's training format. Do not commit collected source text or real examples until dataset redistribution is confirmed.

The answer must be supported by the cited passage, distinguish missing information from negative answers, and avoid inventing dates, fees or eligibility rules. Questions and answers must be independently reviewed against the university source. Separate training and evaluation by source document where possible, and keep the public development questions out of training. A separate unseen holdout is needed for a final generalization claim.

## Decision gate

Before a training run, select a model and deployment constraints; collect and review a sufficiently diverse, authorized corpus; establish an answer-quality baseline with retrieval; and decide whether fine-tuning improves behavior enough to justify the added complexity. Source-level retrieval hit rate alone does not demonstrate a need for fine-tuning. Model-specific costs, privacy and training requirements depend on the selected platform and must be checked then.

Twelve illustrative examples (eleven training and one validation, from five source URLs) are stored locally in the Git-ignored `data/training-v4.jsonl`. The source date records observation, not verified publication. See [STARTER_REVIEW.md](STARTER_REVIEW.md). They passed the validator but are not a training-ready dataset.

Run `python3 -m fast_corpus.cli validate-training --input data/training-v4.jsonl --source-pages data/training-sources-v3.jsonl --holdout data/user-holdout-v2-2026-11-25.jsonl` to verify exact evidence excerpts in the local snapshot and check required fields, exact duplicate questions, source URLs appearing across splits, overlap with the public development questions and expected URLs, and exact question overlap with the supplied local user holdout. An exact text match does not prove evidence supports an answer; the validator cannot detect paraphrases, holdout source overlap without source labels, or URL aliases, verify permissions, or establish dataset quality; human review remains necessary.

The current examples and evaluation are too small to justify a production training run. Do not represent this document as a completed dataset or a trained model.
