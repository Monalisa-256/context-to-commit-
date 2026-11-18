# Context to Commit

**AI Assisted Software Engineering Masterplan**

A coding agent can write a patch, but someone still has to establish what the task required, which version of the code was tested, and what another developer needs to continue the work. Those details are easily lost when the conversation becomes the only record of the job.

Context to Commit is a technical masterplan and an executable reference for keeping software work inspectable across coding sessions. It treats task definitions, source context, decisions, verification results, and handoffs as engineering records rather than messages that must be remembered by an agent.

The methods apply to development with Claude Code, OpenAI Codex, Gemini CLI, OpenCode, or another coding tool. The repository documents how these tools can fit into a common workflow. **The included Python program does not automatically connect to those providers.**

## The engineering problem

Consider a change that passes its tests in the morning. A second session modifies one file in the afternoon, then repeats the earlier claim that everything passed. The claim may be accurate about the old revision, but it is no longer evidence about the current one. Similar problems arise when an agent receives a partial file without its dependencies, when two writers share a checkout, or when a useful decision exists only in a closed chat.

This project develops a practical response:

1. State the task and its acceptance criteria before changing source.
2. Identify the starting revision and separate concurrent work using Git worktrees.
3. Select relevant context with explicit source references and visible omissions.
4. Preserve decisions, proposed memory, and observed evidence as different kinds of records.
5. Associate test results with the source state they actually examined.
6. Produce a handoff that a fresh session can inspect without the old conversation.
7. Keep permissions and approval outside the coding agent's own instructions.

The larger architecture and its limitations are developed in [MASTERPLAN.md](MASTERPLAN.md) and [ARCHITECTURE.md](ARCHITECTURE.md).

## What is available now

The repository contains a complete engineering masterplan, supporting technical documentation, and a local Python reference implementation under [`examples/reading_queue/`](examples/reading_queue/README.md).

The executable example demonstrates a specific defect: completing the same book twice increments a counter twice. Its starter repository contains the defect on purpose. The corrected version, stored alongside it, passes the regression tests. A small command line harness then lets a developer create a task worktree, select context, run checks, audit their applicability, and write a session handoff.

The example uses Python's standard library and Git. It does not require API keys, a model subscription, or a package installation.

| Part | Location | Purpose |
| --- | --- | --- |
| Central plan | [MASTERPLAN.md](MASTERPLAN.md) | Six stages covering foundations, context, continuity, coordination, verification, implementation, and evaluation |
| Executable exercise | [examples/reading_queue/](examples/reading_queue/README.md) | Deliberate failure, corrected source, tests, Git worktree, and handoff |
| Reference tests | [tests/](tests/) | Tests for the harness and the complete published exercise |
| Source consistency check | [tools/sync_reference.py](tools/sync_reference.py) | Confirms the executable listings match `MASTERPLAN.md` and `TESTING.md` |
| Continuous integration | [verify-reference.yml](.github/workflows/verify-reference.yml) | Runs the example and reference tests on Python 3.11, 3.12, and 3.13 |

## Run the tests

You need **Python 3.11 or later**, **Git**, and a terminal. The commands below use `python`. On systems where the executable is named `python3`, use that instead.

```bash
git clone https://github.com/Monalisa-256/context-to-commit-.git
cd context-to-commit-

python tools/sync_reference.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

The root suite contains 24 tests. It checks the reference harness, evidence integrity, source restrictions, task state, and the published exercise from setup through recovery.

Run the seven tests for the corrected reading queue separately:

```bash
cd examples/reading_queue
python -m unittest discover -s tests -v
```

These are the same checks used by the [GitHub Actions workflow](https://github.com/Monalisa-256/context-to-commit-/actions/workflows/verify-reference.yml), which also verifies that the source listings have not drifted from their documentation. The workflow has passed on Python 3.11, 3.12, and 3.13. A successful test run verifies the stated test cases, not every possible failure or security property.

## Reproduce the defect and the repair

The normal test suite uses corrected code. To see why the engineering records matter, create a separate exercise repository from the deliberately defective starter.

From the root of the cloned repository:

```bash
python examples/reading_queue/bootstrap.py ../reading-queue-lab
cd ../reading-queue-lab
python -m unittest discover -s tests -v
```

The last command is **expected to fail** on `test_completion_is_idempotent`. The bootstrap script creates a new Git repository, commits the faulty baseline, and refuses to overwrite an existing directory.

Now create a named task and record its first verification attempt:

```bash
python harness.py start READ01 \
  --goal "Prevent duplicate completion counts" \
  --acceptance "Completing the same book twice counts it once"

python harness.py context READ01 reading_queue.py tests/test_reading_queue.py
python harness.py check READ01
python harness.py audit READ01
```

Both `check` and `audit` should report failure while the defect remains. Make the repair in the task worktree, not in the original exercise checkout. Then rerun the check and audit, and create a handoff. A later source edit should make the earlier passing evidence inapplicable.

The full procedure, including the location of the worktree and the exact correction, is in the [reading queue exercise guide](examples/reading_queue/README.md).

### What the local harness records

| Command | Recorded or observed result |
| --- | --- |
| `start` | Task identity, goal, acceptance criteria, starting revision, and worktree |
| `context` | Selected source, content digests, byte limits, and omission notices |
| `check` | Unit test outcome, process status, output digests, and source mutation information |
| `audit` | Whether the latest evidence is intact, successful, and applicable to the current source |
| `handoff` | Current task state, verification references, and the information needed to resume |
| `propose` | A source linked observation awaiting review, not an approved project rule |

The harness keeps its local runtime files in `.worklog/`. These records are excluded from Git by default. Preserve important results intentionally before discarding a workspace.

## Read the technical documents

| Document | Read it for |
| --- | --- |
| [MASTERPLAN.md](MASTERPLAN.md) | The complete engineering approach, progressive exercises, code listings, and supporting research |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System boundaries, responsibilities, task lifecycle, storage, and provider interface design |
| [IMPLEMENTATION.md](IMPLEMENTATION.md) | Building and extending the local workflow step by step |
| [TESTING.md](TESTING.md) | Test procedures, failure cases, evidence limits, and release checks |
| [SECURITY.md](SECURITY.md) | Trust boundaries, permissions, threat scenarios, and responsible vulnerability reporting |
| [RESEARCH.md](RESEARCH.md) | Primary sources, evidence assessment, proposed measurements, and unresolved questions |
| [ROADMAP.md](ROADMAP.md) | Engineering priorities and acceptance criteria for the larger system |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to submit reproducible corrections, technical changes, and research contributions |
| [CHANGELOG.md](CHANGELOG.md) | Recorded changes and the release history policy |

Readers who are new to coding agents can start with Stage I of the masterplan and then complete the reading queue exercise. Developers evaluating an existing workflow may prefer the architecture, testing, and security documents first.

## Scope and security

The code is a **local educational reference**, not an unattended coding agent service.

It currently demonstrates task worktrees, explicit context selection, verification receipts, evidence audits, source linked proposals, and neutral handoffs. It does **not** include live provider adapters, authenticated approvals, protected shared memory, distributed task ownership, or a secure remote runner.

A Git worktree separates working directories but does not confine a process. The harness executes Python unit tests with the privileges of the person running it. Its file checks and local hashes are useful for detecting specific problems, but they do not establish a complete security boundary or independently protected audit trail. **Do not run untrusted repository code through this example.**

Read [SECURITY.md](SECURITY.md) before extending the runner, accepting untrusted inputs, or publishing a vulnerability. The research and roadmap documents distinguish what has been demonstrated from what still needs implementation and evaluation.

## Contributing and licence

Corrections are welcome when they identify a reproducible problem, clarify a source, strengthen a test, or improve the engineering method. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Do not include credentials, private repository content, or exploit details in public reports.

Context to Commit is distributed under the [MIT License](LICENSE).
