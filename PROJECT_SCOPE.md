# Project scope

## Purpose and audience

Build a documented, reproducible pipeline for collecting and preparing eligible public FAST-NUCES information, and evaluate whether it can support a source-linked information assistant. The first audience is both prospective and current students. This is an independent portfolio project, not an official university service.

## Questions to support

- Prospective students: which programs are offered, what eligibility requirements apply, how to apply, and where to find admissions schedules, fees and financial assistance.
- Current students: where to find academic rules, financial policies, student services and publicly available handbooks.
- Answers should retain campus, program and academic-year context where provided, link to supporting sources, and acknowledge when the source does not establish an answer. Dates, fees and policies require current-source verification.

## Initial collection boundary

The initial candidate seed and exact host are `https://www.nu.edu.pk/` and `www.nu.edu.pk`. This is a proposed scope, not a finding that collection or training is permitted. Task 4 must inspect current host-specific robots rules, redirects, terms and permissions before the pilot. A redirect to `nu.edu.pk` or a campus subdomain is outside the initial allowlist until separately reviewed and deliberately added. Scope can expand only after documenting each host's rules and intended use.

Start with public HTML pages relevant to the questions above. Public text-based PDFs such as handbooks are candidates for a later task after rights and access are checked. Exclude authenticated portals, forms and submissions, private records, third-party domains and material, and unrelated bulk collection. Do not bypass access restrictions. Review personal information, copyright and reuse rights before dataset publication or model training.

## Deliverables and success criteria

1. A bounded, configurable collection pipeline with source and run metadata, failure reporting, automated tests and documented operating instructions.
2. Cleaned, deduplicated, source-linked documents and chunks, with extraction quality reviewed against a documented sample.
3. A held-out set of representative questions and a retrieval baseline with reported methods, results, source support and failure cases.
4. A reproducible portfolio description with honest limitations. Fine-tuning is a later, evidence-based decision, not a prerequisite for calling the collection pipeline complete.

## Open decisions

- Whether and under what conditions FAST permits the intended collection, training and any redistribution; robots access alone does not settle reuse rights.
- Whether the main host redirects or links to another host required for useful coverage; assess in Task 4.
- The size of the live pilot, the exact evaluation set and measurable performance targets; set these after site inspection and initial quality review rather than inventing numbers.
- The contact identity for the crawler and any selected GitHub repository; obtain these before they are needed.
