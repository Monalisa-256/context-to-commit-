# Research, Evidence and Open Questions

Context to Commit proposes a practical way to develop software with coding agents while keeping engineering decisions, work in progress and test results outside any single conversation. This document explains the evidence behind that proposal, the limits of that evidence and the experiments needed to establish whether particular practices help.

The primary technical plan is [MASTERPLAN.md](MASTERPLAN.md). [ARCHITECTURE.md](ARCHITECTURE.md) states the intended system, [IMPLEMENTATION.md](IMPLEMENTATION.md) describes the runnable learning exercise, [TESTING.md](TESTING.md) defines its checks, and [SECURITY.md](SECURITY.md) gives the security boundary. This document does not replace any of those files. It records what can reasonably be concluded from published material and what still requires local measurement.

## 1. How to read the evidence

A recommendation can be reasonable without having been proved superior in a controlled experiment. Much of the engineering described in this repository falls into that category. Labelling the difference protects readers from treating a useful design as a measured scientific result.

The evidence is divided into five classes:

| Label | Kind of evidence | Suitable claim | Limit |
|---|---|---|---|
| `DOC` | Official product or protocol documentation | A documented interface or control exists | An installed version or configuration may behave differently |
| `STUDY` | Published experimental research | Researchers observed an effect under described conditions | The effect may not generalise to other models or repositories |
| `STANDARD` | Security, development or provenance standard | A control or assurance framework is defined | Following a few recommendations does not prove compliance |
| `LOCAL` | Reproducible commands and tests against the sample | A particular command gave an observed result in a specified environment | Local tests cannot establish production security or universal performance |
| `DESIGN` | Proposed engineering policy derived from failure analysis | A mechanism is recommended for an identified risk | Its cost and benefit still need measurement |

A product announcement and an independent study should not receive the same weight. A documentation page is authoritative about the interface its maintainer describes, not a neutral performance comparison. An open source project's unit tests can demonstrate a behaviour without proving resistance to an attacker who controls the machine running them.

### Research procedure

For each important claim:

1. Identify the exact question rather than collecting material by topic alone.
2. Prefer the protocol specification, primary study, official manual or original technical analysis.
3. Record which behaviour or finding the source supports, and which interpretation would go beyond it.
4. Separate requirements inherited from established engineering practice from experiments specific to coding agents.
5. Check for changing defaults, versioned schemas and product specific caveats.
6. Convert uncertain claims into tests or open questions, rather than smoothing them over.
7. Update the conclusion when a test or new source contradicts it.

The bibliography at the end provides direct links. Source identifiers such as `[R08]` are stable within this file; they are not a claim that the reference is permanently current.

## 2. Findings with immediate consequences

### 2.1 A context window is capacity, not guaranteed comprehension

The *Lost in the Middle* study examined language models performing tasks with information at different positions in long inputs. It found sensitivity to placement on the evaluated tasks [R08]. This is a reason to test retrieval and information layout. It is **not** evidence that every coding agent fails after a fixed number of messages or that 60 percent context usage is a scientifically established renewal threshold.

For Context to Commit, the resulting recommendation is to select current source files, active decisions and relevant error evidence deliberately. A new context package should explain what it contains and what it omits. The context budget belongs to the entire interaction, including tool calls and responses, rather than only to the repository excerpts.

Questions the study leaves open include the performance of particular coding products, the effect of tool based retrieval, and how much context compaction changes results when source files remain externally accessible.

**Proposed validation:** compare full history, brief summary and source selected context across the same tasks. Measure accepted changes, required facts omitted, token usage and reviewer corrections. Do not call smaller context an improvement unless success and safety remain acceptable.

### 2.2 Memory needs update rules as well as storage

LongMemEval studies memory across sustained conversations, including information retrieval, reasoning, temporal understanding, updated facts and appropriate abstention [R09]. The lesson for engineering is not that a database or embedding search solves forgetting. The difficult cases are often *which fact is current*, *why it should be trusted* and *when the system should say it does not know*.

This motivates four distinct records in the masterplan: project knowledge, reviewed decisions, task state and evidence history. An inferred explanation is a proposed observation. An accepted decision needs a source and a reviewer. A superseded decision must remain discoverable for history without being treated as current policy.

The LongMemEval tasks are not a direct measurement of software project memory systems. Consequently, a claim that the proposed ledger prevents all memory loss would be unsupported.

**Proposed validation:** retain a decision across several sessions, explicitly replace it, add a conflicting old summary and restart with a different agent. Score whether the current decision is selected with its source, whether the old one is rejected and whether uncertainty is reported.

### 2.3 Agent interoperability has more than one layer

The Model Context Protocol, MCP, concerns how clients access tools, prompts and data resources. Its specification and security documentation address transport and authorisation questions, but the exact requirements depend on the negotiated protocol revision [R05][R18]. The Agent Client Protocol, ACP, concerns interactions between a client and a coding agent, including session events and control messages [R06].

Neither standard makes sessions universally portable. Neither guarantees that two agents have identical filesystem access, cancellation behaviour, event formats, approval semantics or retained state. A common JSON wrapper around vendor commands is therefore an *adapter contract*, not proof of interoperability.

The masterplan proposes a neutral handoff containing task identity, source revision, context selection, active decisions, evidence and pending work. The first measure of portability should be whether a new session can continue from those records without the old transcript. Full provider automation should follow only after real adapters pass conformance and interruption tests.

**Proposed validation:** use one agent to implement a bounded change and a different agent to review or continue it. Start the second agent without the first agent's conversation. Compare findings against a human reviewer and actual test results.

### 2.4 Permissions cannot depend on wording alone

OWASP identifies prompt injection and excessive agency among risks facing applications that connect language models to tools [R10][R17]. This supports keeping authority in policy checks and restricted execution, rather than relying only on natural language instructions. Git worktrees are valuable for separating branches, but the Git manual makes no claim that a worktree restricts operating system privilege [R12].

A coding agent that can invoke tests may execute arbitrary test code. A tool label marked read only does not replace inspection of its actual downstream effects. Access to credentials, filesystem paths, network services and CI tokens must be constrained where actions occur. Security is a series of enforceable boundaries, not a statement that an agent should be careful.

The educational `harness.py` has a fixed test command and limited context path selection, but it executes as the calling user. Its local test receipt is not protected against someone with write access to both the receipt and its checksum. [SECURITY.md](SECURITY.md) lists the controls required before unattended execution.

**Proposed validation:** run harmless synthetic attacks against a disposable sandbox. Attempt an out of scope file read, a forbidden network call, an injected instruction and a forged receipt. Observe OS and service denials, not just an agent's written refusal.

### 2.5 Verification must name what was verified

A passing command establishes that the command returned successfully for some input state in a particular environment. It is not a universal correctness certificate. A later source edit, changed dependency or missing evidence file can make the record unsuitable for deciding whether the current code is ready to merge.

The masterplan's reference code calculates a digest over Git tracked and nonignored untracked files, with additional metadata. It records the test exit status and whether the workspace changed during execution separately. This directly addresses an earlier implementation flaw in which a failed check that changed files could be described mainly as stale. [TESTING.md](TESTING.md) contains automated checks for this distinction.

The manifest does not capture every possible build input. Ignored files, environmental dependencies, remote services and filesystem races remain outside its guarantee. A stronger release process should document the input set, use an isolated builder and protect receipts independently. SLSA describes progressively stronger build provenance and verification models [R13].

**Proposed validation:** produce a passing check, change one source byte, and confirm that audit fails. Then deliberately create a test that mutates a file and exits unsuccessfully; confirm that the receipt reports both the failure and the mutation.

### 2.6 Public coding benchmarks are not a substitute for project evaluation

Published evaluation sets make model comparisons possible, but their tasks, tests and labels can have defects. OpenAI's technical analysis of coding evaluations reports flaws found during an audit of SWE Bench Pro [R11]. The report is a source authored by a provider with a stake in the evaluation landscape, so its methods and findings should be read critically. It is sufficient to illustrate why benchmark data quality deserves inspection; it does not establish that a different provider is generally better or worse.

For this repository, the unit of measurement should be an *accepted engineering change*. Acceptance includes the requirement, current source identity, checks, review and relevant risk constraints. We should report the number and diversity of test tasks, not only a headline success percentage.

**Proposed validation:** construct a private task suite with real bug fixes, feature work, architectural changes, interruptions and security cases. Keep the holdout tasks outside agent memory. Compare workflows with the same acceptance tests and matched resource budgets.

## 3. Source to decision register

This table connects a source to a decision in the project. It is intentionally more specific than a link directory.

| Decision or claim | Evidence | Classification | Reasonable conclusion | What remains unproved |
|---|---|---|---|---|
| Use worktrees to separate task branches | Git worktree manual [R12] | `DOC` | Multiple working trees can hold different checkouts | Worktrees stop untrusted processes escaping their directories |
| Keep instructions in native provider surfaces | Claude Code, Codex, Gemini CLI and OpenCode docs [R01] to [R04] | `DOC` | Each product has relevant project guidance mechanisms | The same file content loads identically across vendors |
| Separate tools from agent client communications | MCP and ACP sources [R05][R06] | `DOC` | Different protocols solve different integration problems | A single adapter automatically covers every provider |
| Prefer selected context over transcript accumulation | Lost in the Middle [R08] plus design analysis | `STUDY` + `DESIGN` | Attention to retrieval and placement is warranted | Every smaller context package improves coding accuracy |
| Track memory validity and supersession | LongMemEval [R09] plus engineering design | `STUDY` + `DESIGN` | Long interaction memory needs update and abstention tests | An evidence ledger eliminates all forgotten information |
| Enforce permissions outside the model | OWASP and vendor security guidance [R10][R17][R19] | `STANDARD` + `DOC` | Tool rights and execution boundaries require independent control | A prompt restriction alone blocks malicious actions |
| Tie checks to current source | Masterplan local reference and testing specification | `LOCAL` + `DESIGN` | Old checks can be rejected after a source change | Local file hashes are independent attestation |
| Review benchmark validity | Coding evaluation audit [R11] | Published technical analysis | Dataset errors can distort conclusions | Any public benchmark is universally invalid |
| Protect CI inputs and permissions | GitHub and OpenSSF [R14][R20] | `DOC` + `STANDARD` | Untrusted workflows and broad tokens deserve controls | A passing repository security score guarantees safety |
| Use protected provenance for significant releases | SLSA 1.2 [R13] | `STANDARD` | Trusted builder and consumer checks strengthen evidence | The sample implementation satisfies any SLSA level |
| Use structured tool requests | Python subprocess documentation [R15] | `DOC` + `DESIGN` | Command arrays can avoid unnecessary shell interpretation | A command array makes running untrusted tests safe |
| Evaluate economic outcomes across full tasks | Cost model in the masterplan | `DESIGN` | Cost per accepted change is a useful metric | A particular model is always cheapest for a role |

An update to a cited product interface should trigger a review of affected rows. A new benchmark result should trigger an evaluation design review, not an immediate change to the default agent.

## 4. What the existing sample actually establishes

The local exercise uses a small Python reading queue and an intentionally failing completion operation. The teaching program in `MASTERPLAN.md` manages tasks from the primary checkout while each task has a separate worktree. Its functions provide a clear subject for testing without requiring a model subscription.

The test coverage described in [TESTING.md](TESTING.md) includes task creation, bounded context packages, audit exit codes, source changes after a pass, failing checks that also modify source, context path restrictions, tampered receipts and handoff creation. That is evidence of the sample's defined behaviour **when those tests are executed against the specified code and environment**. It is not an external multi agent benchmark or a penetration test.

To reproduce a claim, a reader should preserve:

```text
Repository revision:
Python and Git versions:
Operating system:
Commands executed:
Environment and installed dependencies:
Task identifier:
Source manifest coverage:
Test exit codes:
Observed source mutation:
Evidence paths and checksums:
Result of audit:
Known inputs outside the manifest:
```

If any of these are unavailable, say what is missing. Do not replace an absent execution record with an agent's description of what it believes happened.

### Four local findings and their limits

**The audit uses an actual process exit status.** That makes it usable as a CI gate in principle. The gate can still only evaluate the local receipt and source coverage its implementation understands.

**Tests can fail while changing source.** The current sample records these as distinct facts. It does not restore files automatically; manual review decides what to retain.

**An old pass can become inapplicable.** Editing covered source changes the manifest and causes an audit refusal. A change to an ignored environmental input may not be detected.

**A neutral handoff can be generated.** It carries task and source information into another session. The sample does not itself connect to Claude Code, Codex, Gemini CLI or OpenCode, so automated portability across providers is not yet demonstrated.

These distinctions should remain visible whenever the repository is presented publicly.

## 5. Provider research

### Claude Code

The documented surfaces include project guidance through `CLAUDE.md`, lifecycle hooks and a permission system [R01]. Its security and sandboxing documentation distinguishes model/tool permission decisions from operating system boundaries [R19]. This is useful for a local coding workflow, but it does not authorise us to claim that every mode or platform confines every tool.

**Implementation question:** Which tool calls are covered by the active sandbox on each supported operating system, and how are denials surfaced to the controlling application?

**Acceptance test:** start with a deliberately restrictive policy, attempt prohibited file and network operations, and record the actual result for the installed version. Then exercise cancellation and a resumed task.

### OpenAI Codex

Codex offers noninteractive execution and programmatic integration routes, including components aimed at event handling, sessions and approvals [R02]. It is reasonable to treat these as candidate adapter surfaces. Their runtime behaviours still need to be measured under the exact policies selected by the project.

**Implementation question:** Can an adapter consistently distinguish provider process completion, paused approval, tool failure and successfully verified code?

**Acceptance test:** execute a bounded read only task, then a source edit task, with approvals and cancellation observed through the documented interface. Do not treat a normal process exit as verified feature completion.

### Gemini CLI

Gemini CLI documents project context, headless operation, checkpointing, trusted folders and sandbox options [R03][R21]. A built in checkpoint can help resume a vendor session, but it should not replace the project's own task and evidence records.

**Implementation question:** Which settings control tool execution and workspace trust in the installed revision, including headless mode?

**Acceptance test:** compare effective permissions between an untrusted folder and an explicitly trusted task worktree. Validate the resulting tool outcomes rather than assuming their names imply behaviour.

### OpenCode

OpenCode documents agent definitions, tool permissions and conversation compaction [R04]. These make it a candidate for role specific work and scripted runs. Its own compaction scheme should be treated as a provider facility, not as the project's authoritative long term memory.

**Implementation question:** Are effective permissions determined by project, user and administrator configuration in a way the adapter can inspect and test? What happens to nested tools and plugins?

**Acceptance test:** configure a read only reviewer, attempt a source write and record whether the action is blocked at the tool boundary.

### Cross provider comparison

Do not choose a permanent winner on reputation. The useful comparison is task class performance under declared conditions: correctness, missed requirements, review findings, tool errors, human repair effort, cost, elapsed time and recovery after interruption. Agent versions, model selection, permissions and context packages must be recorded so differences can be interpreted.

## 6. Method for evaluating context and continuity

A useful task suite contains more than a handful of bug fixes. Include feature requests with ambiguous requirements, changes that cross several files, dependency conflicts, testing failures, long runs with a deliberate interruption and tasks requiring older architectural decisions.

### Experimental groups

| Comparison | Baseline | Treatment | What it isolates |
|---|---|---|---|
| Context selection | Recent conversation plus ad hoc file reads | Rebuilt context with source provenance | Whether explicit retrieval improves results |
| Memory | Conversation summary only | Source backed decisions and task ledger | Whether durable records improve recovery |
| Agent switching | Same agent in a fresh session | Different provider with the same handoff | Portability and provider effects |
| Review | Implementer self review | Independent reviewer with contract and diff | Incremental defect discovery |
| Verification | Test success message | Source bound receipt and audit | Stale evidence and false completion detection |
| Parallelism | One writer | Multiple disjoint worktrees | Time savings versus integration cost |

Comparisons that alter model, context, budget, tool access and reviewer simultaneously are difficult to interpret. Change one major variable at a time where practical. Use the same acceptance tests and equivalent review standards. Randomise task order and report unsuccessful runs, not just completed tasks.

### Measurement definitions

Let `A` be the number of independently accepted tasks and `T` the number assigned. The verified completion rate is `A / T`. Do not omit blocked, timed out or abandoned tasks from `T` without explaining the exclusion rule.

Let `C` be the total billed model use, runner expense and measured review/rework cost. Cost per accepted task is `C / A` when `A > 0`; otherwise report it as undefined along with total expense.

Recovery success is the fraction of interrupted tasks a receiving session completes without access to the original conversation, under the same final acceptance standard. Record unnecessary repeated work and any incorrect assumptions imported from the handoff.

A complete report should name the repository revision, model and tool versions, task categories, sample size, acceptance procedure, limits, and uncertainty. Raw percentages without a denominator and test description should not be used as evidence of improvement.

## 7. Research questions worth answering

| ID | Question | Why it matters | Minimal experiment |
|---|---|---|---|
| Q01 | Which source retrieval method offers the best verified completion at a fixed token budget? | Prevents context bloat | Compare symbol search, semantic search and combined retrieval |
| Q02 | At what point does session renewal save more work than it costs? | Optimises long tasks | Vary renewal policy with matched tasks and outcomes |
| Q03 | Can a model switch preserve decisions without importing stale hypotheses? | Tests neutrality of handoffs | Cross provider recovery with deliberate obsolete notes |
| Q04 | How often does cold review find issues missed by self review? | Justifies independent agent expense | Blind defect review across representative changes |
| Q05 | Can a provenance check prevent stale or forged verification from reaching merge? | Supports release integrity | Inject changed files and tampered receipts into CI |
| Q06 | Which test and build inputs are missed by the source manifest? | Exposes reproducibility gaps | Vary ignored files, environment, dependencies and remote fixtures |
| Q07 | How do different providers react to identical permission constraints? | Establishes adapter safety | Negative tests on each installed agent revision |
| Q08 | How can memory conflict resolution avoid preserving an incorrect rule? | Limits long lived errors | Supersede decisions and insert conflicting evidence |
| Q09 | When does parallel work create more integration cost than elapsed time saved? | Prevents speculative orchestration | Compare serial work with dependency separated writers |
| Q10 | What data remains exposed through context, logs or provider telemetry? | Determines privacy controls | Data flow audit with synthetic canary values |
| Q11 | Does smaller output summarisation hide diagnostic information? | Balances cost and debugging | Compare full logs with structured failure extracts |
| Q12 | Can the system recover exactly once after an ambiguous remote timeout? | Prevents repeated external side effects | Local idempotent service with injected lost acknowledgements |

These questions are appropriate for issues, pull requests and technical investigations. They should not be presented as already answered by the masterplan.

## 8. Research quality and maintenance rules

A new claim should carry its evidence type and, where meaningful, a repeatable method. The following cases deserve particular scrutiny:

- **Marketing statistics:** ask for task definitions, sampling, baseline and independent replication. Do not repeat an unsupported percentage as a finding.
- **Vendor benchmarks:** check the tested configuration, data set and possible incentives. Prefer primary methodology and reproduction details over ranking summaries.
- **Preprints:** identify whether the work was peer reviewed, what populations it studied and whether later studies challenge its conclusions.
- **Product documentation:** tie statements to a specific interface and version when operationally important. Defaults and configuration names change.
- **Security checklists:** identify the exact trust boundary and an observable negative test. Compliance language without enforcement is weak evidence.
- **Local demonstrations:** preserve complete exit codes and environment information. A successful exercise does not establish production readiness.

When new research contradicts a recommendation, update the affected section, the source to decision register and any tests that encode the older assumption. A corrected statement is more valuable than retaining a polished but unsupported claim.

### Suggested format for a new research note

```markdown
### Claim under review
<Precise statement>

**Category:** DOC / STUDY / STANDARD / LOCAL / DESIGN
**Source:** <Direct primary reference>
**Relevant method or interface:** <What was actually examined>
**Finding:** <What the evidence supports>
**Limitations:** <What it cannot establish>
**Impact on the repository:** <Decision or test to reconsider>
**Reproduction:** <Command or protocol when applicable>
**Review status:** Proposed / Checked / Rejected / Superseded
```

A source register is useful only if it can change engineering decisions. Do not let it become a passive collection of links.

## 9. Annotated source register

The references below identify sources behind the project. Some are peer reviewed studies; others are living documentation or standards. Their roles differ. Publication years in citations identify the original research; they are not an edition date for Context to Commit.

### Coding agents and interfaces

**[R01] Anthropic, Claude Code documentation.** [Project memory](https://code.claude.com/docs/en/memory), [hooks](https://code.claude.com/docs/en/hooks), [permissions](https://code.claude.com/docs/en/permissions). Documents the provider's instruction and tool control surfaces. Relevant to adapter and project guide design. Does not prove cross provider equivalence.

**[R02] OpenAI Developers, Codex documentation and architecture.** [Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform), [repository instructions](https://developers.openai.com/codex/guides/agents-md), [sandbox security](https://developers.openai.com/api/docs/guides/agents-api/environments/security). Establishes supported integration options and the distinction between execution, sessions and approvals. Not a benchmark of other coding agents.

**[R03] Gemini CLI project documentation.** [Headless operation](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/headless.md), [checkpointing](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/checkpointing.md), [project context](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md). Product interfaces require revision-specific checking.

**[R04] OpenCode documentation.** [Agents](https://opencode.ai/docs/agents/), [permissions](https://opencode.ai/docs/permissions), [compaction](https://opencode.ai/docs/compaction). Supports the discussion of roles, configurable tool control and lossy conversation summarisation.

**[R05] Model Context Protocol project.** [Specification and documentation](https://modelcontextprotocol.io/) and [the 2026 protocol revision](https://blog.modelcontextprotocol.io/posts/2026-07-28/). Concerns tool and resource connections, not guaranteed task portability between products.

**[R06] Agent Client Protocol project.** [Official protocol overview](https://github.com/agentclientprotocol/agent-client-protocol/blob/main/docs/protocol/v2/overview.mdx) and [project repository](https://github.com/agentclientprotocol/agent-client-protocol). Describes a client to agent communication interface. Do not infer consistent sandboxing from protocol compatibility.

**[R07] GitHub Docs.** [Mermaid diagrams in Markdown](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams). Documents source editable diagrams supported in GitHub's Markdown renderer. It does not make arbitrary Markdown executable.

### Context, memory and evaluation

**[R08] Liu et al., “Lost in the Middle: How Language Models Use Long Contexts.”** *Transactions of the Association for Computational Linguistics*, 2024. [ACL Anthology](https://aclanthology.org/2024.tacl-1.9/). Empirical motivation for evaluating information location and retrieval; not a universal numerical limit for coding agents.

**[R09] Wu et al., “LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory.”** *ICLR*, 2025. [Conference paper](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html). Tests sustained conversational memory and updates. Results cannot be directly transferred to the repository's proposed memory ledger without local evaluation.

**[R10] OWASP.** [Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/). A security risk classification used to identify prompt injection, excessive permissions and related weaknesses. A taxonomy is not a product security certification.

**[R11] OpenAI, “Separating signal from noise in coding evaluations.”** [Technical analysis](https://openai.com/index/separating-signal-from-noise-coding-evaluations/). Discusses coding benchmark task quality and evaluation defects. Treat as a provider authored analysis with a disclosed source context.

### Software engineering and security

**[R12] Git project.** [git-worktree documentation](https://git-scm.com/docs/git-worktree). Establishes behaviour of separate working trees sharing one repository. It does not provide process confinement.

**[R13] SLSA project.** [Specification version 1.2](https://slsa.dev/spec/v1.2/), [build provenance](https://slsa.dev/spec/v1.2/build-provenance), [verification](https://slsa.dev/spec/v1.2/verifying-artifacts). Provides assurance requirements for build evidence, builder identities and consumers. The educational harness does not claim any level.

**[R14] GitHub Docs.** [Secure use of GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use). Covers workflow permissions, untrusted inputs and safe dependency handling. Relevant when turning local examples into CI.

**[R15] Python Software Foundation.** [Subprocess management](https://docs.python.org/3/library/subprocess.html) and [unittest](https://docs.python.org/3/library/unittest.html). Defines the process and test interfaces used by the reference program. Neither supplies operating system sandboxing.

**[R16] NIST.** [Secure Software Development Framework, SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final). Broad software development security practices. Applicable to secure planning and implementation but not specific proof of coding agent reliability.

**[R17] OWASP Cheat Sheet Series.** [MCP Security](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html). Discusses tool, transport and authorisation risks at MCP boundaries. Use with the relevant official protocol revision.

**[R18] Model Context Protocol project.** [Security best practices](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/docs/2026-07-28/tutorials/security/security_best_practices.mdx) and [authorisation considerations](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/basic/authorization/security-considerations.mdx). Official protocol level guidance. SDK features may differ from specification capabilities.

**[R19] Anthropic.** [Claude Code sandboxing](https://www.anthropic.com/research/claude-code-sandboxing). Explains a provider's approach to reducing tool authority. Not independent verification of every environment or setting.

**[R20] OpenSSF.** [Scorecard checks](https://github.com/ossf/scorecard/blob/main/docs/checks.md). Supplies checks and rationale for repository security practices, including dependencies and workflow token scope. Scorecard results are heuristics, not a complete audit.

**[R21] Gemini CLI project.** [Sandbox settings](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/sandbox.md) and [trusted folders](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/trusted-folders.md). Describes vendor safety mechanisms. Actual behaviour needs installed version testing.

**[R22] OpenCode.** [Tool documentation](https://opencode.ai/docs/tools) and [configuration](https://opencode.ai/docs/config). Relevant to adapter capability negotiation and effective permissions; project settings alone do not establish OS confinement.

**[R23] GitHub Docs.** [Private vulnerability reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository). Explains the reporting channel used in the proposed security policy. The repository maintainer must actually enable it.

**[R24] NIST.** [AI Risk Management Framework: Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence). Broad risk management considerations. It should guide risk discovery rather than be presented as a certification of this project.

## 10. Claims this project does not make

Context to Commit does not establish that any coding agent is the most reliable across all tasks. It does not establish an optimum context window utilisation, that summaries are always harmful, that two models are always better than one, or that switching between vendors eliminates memory loss. It does not claim that a Git worktree is a sandbox, that a checksum is a signed attestation, or that one passing test proves a feature safe to release.

The local reference is a controlled learning example. Its value is that failures and missing evidence can be made visible. The broader system remains an engineering proposal until its adapters, runner, storage, policies and recovery mechanisms are implemented and measured.

Research should sharpen that boundary, not blur it.
