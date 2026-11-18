# Reading queue exercise

This is the executable example used in [MASTERPLAN.md](../../MASTERPLAN.md). It demonstrates a small, reproducible defect and the records needed to repair it without depending on an earlier coding session.

The directory contains a **corrected reference implementation**, a deliberately defective starter, the local `harness.py` from the masterplan, and tests. The starter is kept separate so the repository's normal test suite stays green.

## Requirements

Python 3.11 or later and Git. No packages need to be installed. This exercise runs Python test code with your normal user permissions. Use a new directory containing only these files, not a repository you do not trust.

## Create a clean exercise repository

From the root of Context to Commit:

```bash
python examples/reading_queue/bootstrap.py ../reading-queue-lab
cd ../reading-queue-lab
```

The bootstrap script refuses to overwrite an existing directory. It creates a new Git repository, commits a deliberately defective baseline, and leaves the main Context to Commit repository untouched.

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

One test must fail: `test_completion_is_idempotent`. The original implementation increments the completion counter every time the same book is marked done.

## Record the failure with the harness

```bash
python harness.py start READ01 \
  --goal "Prevent duplicate completion counts" \
  --acceptance "Completing the same book twice increases the counter only once"
python harness.py context READ01 reading_queue.py tests/test_reading_queue.py
python harness.py check READ01
python harness.py audit READ01
```

At this stage, `check` and `audit` must return unsuccessful exit codes. That is the expected result, not a broken setup. The generated worktree is next to the exercise directory, under `reading-queue-lab_worktrees/READ01`.

## Correct the code

Edit `reading_queue.py` inside the **task worktree**, not the main checkout. Replace the body of `complete` with:

```python
def complete(self, book_id: str):
    book = self.books[book_id]
    if not book["done"]:
        book["done"] = True
        self.completed_count += 1
```

Return to the original exercise directory and run:

```bash
python harness.py check READ01
python harness.py audit READ01
python harness.py handoff READ01
```

All tests should now pass. The audit should succeed because the current source matches the tested state. The handoff appears under `.worklog/handoffs/READ01.md`.

Change the source in the task worktree again and rerun `audit`. It should fail because the earlier evidence no longer applies. Rerun `check` to establish a new observation.

## Review the records

The harness writes task records, selected context, test receipts, and handoffs under `.worklog/`. Git ignores these runtime files by default. Back them up deliberately before discarding the exercise directory. They are not a substitute for versioned architecture decisions or independently protected audit records.

## Run the corrected reference on its own

From the **`examples/reading_queue/`** directory in the publication repository:

```bash
python -m unittest discover -s tests -v
```

That run uses the corrected implementation and should pass without creating a separate exercise repository.

## What the example does not secure

The Git worktree keeps code changes separate, but it is not a security sandbox. The test command can execute arbitrary Python code with your current user's privileges. The program has no provider adapters, remote backup, distributed locks, approval service, or production isolation. Those are design goals described in [ARCHITECTURE.md](../../ARCHITECTURE.md), not features in this example.
