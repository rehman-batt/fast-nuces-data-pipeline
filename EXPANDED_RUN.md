# Expanded collection — 2026-11-25

Following the initial pilot, an authorized run of the exact `www.nu.edu.pk` host used the explicit HTTP-404-only robots policy, a two-second per-origin delay, a 25-page output limit and 35 page-attempt limit. It produced 25 records with 24 unique extracted-text hashes. The local snapshot SHA-256 is `139b1b004ec5247d689ca583caf771ef1b4a6a0217f1e62cc092a1b2c7cd7721`.

The log records one connection closure and one oversized page; those pages were not collected. The successful run stopped at the page limit and is not a complete crawl. Thirteen records have campus-related paths, including supervisor, award and student-list pages that may contain personal information. Those records are kept locally and excluded from the current example set pending relevance and privacy review. The dataset and crawler contact are Git-ignored.

Eight illustrative model-neutral examples (seven training, one validation) were prepared locally from three source pages, separate by URL from the current development-evaluation sources. All eight exact evidence excerpts were found in the snapshot. This is a tiny starter, not sufficient for training or evidence of answer quality; the validator cannot establish semantic correctness, detect all aliases, or verify legal permissions. Dataset publication rights are unconfirmed.
