# Initial evaluation questions

These 12 manually drafted, source-linked questions cover prospective students (9) and current students (3). Source pages and the 10-page pilot were inspected on 2026-11-25. `expected_urls` identify a starting source for retrieval assessment, not a complete ground-truth answer or proof that every passage on the page answers the question. `evidence_goal` states what a reviewer should look for in the passage and answer.

The initial pilot includes the expected source for each of the nine `in_corpus` cases; several cases share a source page. The three student-page sources were not collected in that pilot and are labeled `not_in_corpus`; exclude them from pilot retrieval recall and use them as coverage checks, not automatic proof that an answer must be impossible. Verify the index and reclassify after corpus expansion. Dates, fees and policies can change; recheck sources and assessment labels for each dataset version.

Keep these questions out of fine-tuning data. Because they are public in this repository and may guide development, treat this as an initial development evaluation set, not an independent final benchmark. Before reporting final generalization, create a separate unseen, reviewed holdout. Answer quality must be reviewed for source support and context; finding the right URL alone is not enough.
