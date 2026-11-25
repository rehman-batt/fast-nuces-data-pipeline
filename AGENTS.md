# Agent working instructions

- Read `README.md` and `TASKS.md` before making changes. Treat the existing pipeline as a prototype until Task 1 is complete.
- Work on one numbered task at a time, in order, unless the user directs otherwise. Before implementation, state the task's scope and acceptance criteria; after it, report changes, checks, and remaining limitations.
- Run the tests relevant to each task and add meaningful tests for new behavior. Update `TASKS.md` only when its acceptance criteria are met, recording verification and any follow-up. Do not mark live-site work or evaluation complete without evidence.
- Respect the approved host scope and each host's current crawling rules. Do not bypass access controls or commit scraped content, personal data, secrets, or credentials. Check applicable terms and permissions before collection, training, or publication.
- Use Git to make changes reviewable. Inspect `git status` before editing and preserve existing work. Prefer a focused branch named `codex/task-<number>-<short-name>` and a focused commit for each completed task when the user asks to commit. Do not push, create a remote repository, or alter Git history without user authorization. Never invent test results or metrics.

## Core engineering practices

- Keep changes focused: use one task per branch and pull request where practical. Run relevant checks locally and keep the PR reviewable.
- Maintain automated tests for meaningful behavior and run them in GitHub Actions on pull requests once the remote and CI are configured.
- Keep setup, configuration, dependencies, commands, and run or dataset versions documented so results can be reproduced.
- Preserve source provenance, document access and reuse decisions, and keep credentials, personal data, and unreviewed collected content out of Git.
- Evaluate extraction and retrieval against a documented sample; report actual methods, results, and limitations without inventing metrics.
