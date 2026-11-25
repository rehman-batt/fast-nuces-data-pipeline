# Site inspection — 2026-11-25

Scope: the initial proposed host `www.nu.edu.pk`. Responses below were checked on 2026-11-25; website behavior may change. This was a small read-only inspection, not a site crawl.

- [Homepage](https://www.nu.edu.pk/): direct HTTP `200`, `text/html`, with no redirect in the inspected response. Navigation includes admissions, fees, eligibility, academic rules and campus sites. Campus sites use separate hosts and are outside the initial allowlist.
- [robots.txt](https://www.nu.edu.pk/robots.txt): direct HTTP `404`. This does not establish permission for the intended collection, training or redistribution. The prototype deliberately fails closed on this response, so a live crawl of this host currently produces no pages. Any change to that conservative policy needs a documented decision and tests.
- [Sitemap](https://www.nu.edu.pk/sitemap.xml): HTTP `200`, `text/xml`; it contained one URL, `https://nu.edu.pk/`, on the separate apex host. The initial allowlist does not include that host. Do not infer its crawling rules from the `www` host.
- The user reports that FAST authorized use of its website data to build a student-query chatbot. The applicable site terms and permission for publishing or redistributing the dataset separately remain unverified. A search did not establish terms applicable to this host; campus-specific terms must not be assumed to apply here. A useful starting point for a clarification request is the university's [contact page](https://www.nu.edu.pk/home/ContactUs).

## Before the live pilot

Document the reported permission and any operating conditions, confirm permission before publishing or redistributing a dataset, decide how to handle the missing robots file, and supply a contactable crawler user agent. Recheck relevant rules immediately before collecting. Do not collect authenticated content, bypass access controls or publish collected material without reviewing rights and privacy. The absence of a robots file does not itself grant a content license.

Task 4 records findings and open decisions; it does not authorize or establish legal permission for a live crawl. Technical implementation and tests can continue using synthetic fixtures while these questions are unresolved.
