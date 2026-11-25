# Pilot crawl — 2026-11-25

The user reported FAST authorization to use website data to build a student-query chatbot and supplied a contact for the crawler. The initial candidate host was `www.nu.edu.pk`. Dataset redistribution remains unconfirmed.

## Run and outcome

- A first bounded attempt collected zero pages because the connection reset while retrieving `robots.txt`. The crawler failed closed; its output and log were retained locally.
- A separate recheck returned HTTP 404 for `https://www.nu.edu.pk/robots.txt`. One retry used the explicit 404-only policy, a two-second per-origin delay, a maximum of 20 page attempts, and a limit of 10 extracted pages. It collected 10 pages and stopped at the page limit. The log reported no page-fetch failures in that successful run.
- The pages covered the homepage and admissions topics including programs, schedule, eligibility, financial assistance, test pattern, fees and prospectus. They were stored locally under ignored `data/`; the crawl data and contact address are not committed.
- The 10 page records have 9 distinct extracted-text hashes: `/` and `/Home` have identical extracted text. Deduplication should preserve both source URLs (Task 14).

## Initial extraction review

All ten records had a title and non-empty text. Inspection of the starts of records found a leading Unicode BOM and repeated breadcrumb text; the homepage text is approximately 75,000 characters. The existing parser does not preserve tables as structured data; fees and schedules need manual comparison and dedicated tests before use in answers (Tasks 10–11). The prospectus page lists sections, but this pilot does not extract linked PDF content (Task 12). This small sample is not a coverage or accuracy measurement.

The 404 policy applies only when opted in and only to HTTP 404; access-denied, server and network failures continue to fail closed. Check robots and site conditions again before further collection. The pilot establishes that a limited crawl can run; it does not establish model quality or permission to publish the dataset separately.
