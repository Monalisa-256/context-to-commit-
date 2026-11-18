# Context to Commit

### AI Assisted Software Engineering Masterplan

Good code is only part of a completed task. Someone also needs to know why the change was made, which files were involved, what was tested, and whether the result still holds after the next edit.

**Context to Commit** is an engineering masterplan for working with coding agents without handing over those responsibilities. It covers the decisions and records that make software work understandable, verifiable, and recoverable across sessions. The material applies to a developer working alone as well as a team using several coding agents.

The main document is [MASTERPLAN.md](MASTERPLAN.md). It starts with a small Python project, develops a disciplined workflow around it, and moves toward a fuller system for context control, durable decisions, coordinated execution, and independent verification. The supporting documents explain the architecture, reproduce the exercises, set security boundaries, and examine the research behind the design.

This repository contains a detailed technical plan and a local reference program printed in the masterplan. **It is not a deployed coordination service or a production sandbox.**

## What the project addresses

A coding session can end while the task remains unfinished. A later session may lack the original decisions. Two agents may edit the same files. A test result may refer to an earlier revision. A useful source excerpt may arrive without the surrounding assumptions that made it relevant.

The approach here is to make the important state independent of any one conversation:

1. **Define the task.** Record its purpose, scope, exclusions, and acceptance criteria before changing code.
2. **Prepare the workspace.** Establish a known Git revision and give each active writer a separate worktree.
3. **Select context deliberately.** Include relevant source, current decisions, and observed failures, with enough information to find the originals.
4. **Keep decisions and evidence distinct.** A proposed observation is not an approved architectural rule. An agent's report is not a test receipt.
5. **Verify the current source.** Record command results and identify the files they apply to. A later edit invalidates an earlier verification claim.
6. **Preserve a useful handoff.** Save the task, source state, checks, unresolved questions, and next action so another session can continue without the previous chat.
7. **Control consequential operations.** Restrict permissions outside the agent's instructions and require review where the risk demands it.

The aim is not to place more machinery around every change. It is to introduce controls where they solve a failure that developers can actually encounter and reproduce.

## Where to begin

| If you want to | Begin with |
| :--- | :--- |
| Learn the basics of coding with agents | Stage I of [MASTERPLAN.md](MASTERPLAN.md), then the reading queue exercise in [IMPLEMENTATION.md](IMPLEMENTATION.md) |
| Keep work consistent across long conversations | Stage II of the masterplan, particularly context selection, recorded decisions, and session recovery |
| Move work between Claude Code, Codex, Gemini CLI, or OpenCode | Stage III of the masterplan and the coordination design in [ARCHITECTURE.md](ARCHITECTURE.md) |
| Inspect a technical design before building it | [ARCHITECTURE.md](ARCHITECTURE.md) followed by [SECURITY.md](SECURITY.md) |
| Reproduce claims and investigate failures | [TESTING.md](TESTING.md) and the experiment notes in [RESEARCH.md](RESEARCH.md) |

The masterplan is organised into six stages: working foundations; context and continuity; coordination between coding agents; verification and security; building the local reference; and evaluation and maintenance. You can follow them in sequence or use the supporting documents to investigate a particular part of the system.

## Repository documents

| Document | What it contains |
| :--- | :--- |
| [MASTERPLAN.md](MASTERPLAN.md) | The central engineering plan, worked exercises, diagrams, reference code, templates, and research notes |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Component responsibilities, task lifecycle, storage boundaries, context assembly, provider interfaces, and recovery design |
| [IMPLEMENTATION.md](IMPLEMENTATION.md) | The commands for building the reading queue example, extracting the reference program, recording checks, and completing a handoff |
| [TESTING.md](TESTING.md) | Automated and manual verification procedures, expected failures, integrity checks, and test requirements for future components |
| [SECURITY.md](SECURITY.md) | Threat model, permission boundaries, sensitive information handling, disclosure guidance, and limits of the local example |
| [RESEARCH.md](RESEARCH.md) | Source register, research findings, competing approaches, open questions, and proposed comparisons |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to propose changes, report reproducible defects, support technical claims, and prepare reviews |
| [CHANGELOG.md](CHANGELOG.md) | Material changes and the rules for recording actual releases |
| [LICENSE](LICENSE) | MIT licence covering the material in this repository |

The masterplan is the main reading document. The other files have narrower responsibilities and should be read when you need to build, check, challenge, or improve a particular claim.

## Run the local exercise

The first implementation deliberately uses a simple reading queue. Completing an entry twice incorrectly increments a counter twice. The exercise starts with a test that exposes this defect, then follows the repair through an isolated worktree, recorded checks, and a handoff.

You will need **Git**, **Python 3.11 or newer**, and a terminal. The documented shell commands assume a Unix compatible environment. Windows users can follow the same Python steps, with shell syntax adjusted where necessary.

```bash
git clone https://github.com/Monalisa-256/context-to-commit-.git
cd context-to-commit-

python3 --version
git --version
```

Then follow [IMPLEMENTATION.md](IMPLEMENTATION.md) from section 3. It provides the sample application, test files, and an extraction procedure for `harness.py`, whose complete source appears in section 22.3 of [MASTERPLAN.md](MASTERPLAN.md). The exercise runs inside a separate, disposable Git repository. Do not use a repository containing work you cannot afford to lose.

The local program exposes six operations:

| Command | Purpose |
| :--- | :--- |
| `start` | Create a task worktree and save its starting revision |
| `context` | Build a bounded context file from named source paths |
| `check` | Run the fixed local test command and record its outcome |
| `audit` | Check whether the latest receipt is intact and still applies to the current source |
| `handoff` | Save the task state and verification references for a later session |
| `propose` | Record a source linked observation without treating it as approved project policy |

[TESTING.md](TESTING.md) gives the expected results, including cases in which the command **should fail**. A failed baseline test, a changed source file, or altered evidence must not be quietly reported as success.

No external coding agent account is needed to run the local record keeping exercise. Switching between coding agents is a separate, optional experiment. There are currently no tested automatic adapters in the reference program.

## Current scope and limits

The distinction between a working example and a complete system matters here.

| Area | Present in the reference material | Still to be engineered or demonstrated |
| :--- | :--- | :--- |
| Task state | Local task records and Git worktrees | Shared ownership, transactional updates, and crash recovery across machines |
| Context | Explicit file selection, limits, and omission notices | Evaluated retrieval, stronger access controls, and automated context assembly |
| Memory | Proposed observations linked to source files | Reviewed durable knowledge, replacement rules, and protected shared storage |
| Session continuity | Structured local handoff records | Automatic restoration and measured handoffs between live providers |
| Verification | Local test receipts, source checks, and audits | Independent provenance, broader input coverage, and protected execution evidence |
| Agent coordination | Documented roles and neutral interface contracts | Working adapters, enforced reviewer permissions, and cancellation handling |
| Execution security | A threat model and required controls | A tested sandbox, isolated credentials, and authenticated approval services |
| Evaluation | Test procedures and comparison methods | Repeated provider comparisons and published task level results |

Git worktrees separate working copies. They do not restrict what a process can read, execute, or send over the network. Likewise, a local file digest can detect changes without proving that the person or process writing the evidence was trustworthy. These limitations are discussed in [SECURITY.md](SECURITY.md) and [TESTING.md](TESTING.md).

## Research and review

The design draws on official coding agent documentation, established software engineering practices, research into context and memory, and security guidance for systems that execute model selected actions. The sources, their limits, and the experiments still needed are recorded in [RESEARCH.md](RESEARCH.md).

A design recommendation is not presented as a measured performance gain. Claims about reliability, cost, or better results from multiple agents need task level evidence, an identified starting revision, and a test method someone else can repeat.

## Contributing

Corrections to commands, broken examples, missing edge cases, security tests, and well supported research findings are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md) for the review requirements and expected evidence.

Please do not publish a vulnerability or exposed credential in an ordinary issue. Use the private reporting procedure described in [SECURITY.md](SECURITY.md).

## Licence

The repository is distributed under the [MIT License](LICENSE). Preserve the licence and copyright notice when redistributing material covered by it.
