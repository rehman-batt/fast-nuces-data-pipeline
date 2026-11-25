# Fine-tuning data design

Status: planning, not a training-ready dataset. The current corpus is a 10-page pilot; retrieval has only a small source-level development score, and no model answer quality has been evaluated. The user has not yet selected a model or platform; work is proceeding in a model-neutral format.

## Proposed model-neutral record

Each reviewed training example should include an instruction or user question, the desired assistant response, a source URL, the source passage or a stable passage identifier, the source date or collection version, and any campus, program or academic-year context needed to interpret the answer. The current neutral JSONL format uses `question`, `answer`, `evidence`, `source_url`, `source_date` (YYYY-MM-DD) and `split` (`train` or `validation`). Final serialization must follow the selected model or platform's training format. Do not commit collected source text or real examples until dataset redistribution is confirmed.

The answer must be supported by the cited passage, distinguish missing information from negative answers, and avoid inventing dates, fees or eligibility rules. Questions and answers must be independently reviewed against the university source. Separate training and evaluation by source document where possible, and keep the public development questions out of training. A separate unseen holdout is needed for a final generalization claim.

## Decision gate

Before a training run, select a model and deployment constraints; collect and review a sufficiently diverse, authorized corpus; establish an answer-quality baseline with retrieval; and decide whether fine-tuning improves behavior enough to justify the added complexity. Source-level retrieval hit rate alone does not demonstrate a need for fine-tuning. Model-specific costs, privacy and training requirements depend on the selected platform and must be checked then.

Three illustrative examples (two training and one validation, from separate source URLs) are stored locally in the Git-ignored `data/training-starter.jsonl`. They passed the validator but are not a training-ready dataset.

Run `python3 -m fast_corpus.cli validate-training --input data/training-starter.jsonl` to check required fields, exact duplicate questions, source URLs appearing across splits, and overlap with the public development questions and expected URLs. The validator cannot prove evidence supports an answer, detect paraphrases or URL aliases, verify permissions, or establish dataset quality; human review remains necessary.

The current corpus, examples and evaluation are too small to justify a production training run. Do not represent this document as a completed dataset or a trained model.
