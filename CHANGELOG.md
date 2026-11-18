# Changelog

This file records changes that matter to people reading, running, or contributing to Context to Commit. It is not a copy of the Git commit history and it is not a list of planned features. For unfinished work and its acceptance criteria, use [ROADMAP.md](ROADMAP.md).

Changes are grouped under **Unreleased** until a maintainer creates an actual Git tag and publishes a release. The entries below describe the initial documentation set being prepared. They should be checked against the files present in the repository before publication. No version number, release date, or existing Git tag is asserted here.

## Unreleased

### Added

**Engineering material**

- `MASTERPLAN.md`: the central plan for developing software with coding agents, including task contracts, Git worktrees, context selection, long session recovery, project memory, agent coordination, permissions, verification, and the reading queue exercise.
- `ARCHITECTURE.md`: the component and trust boundaries of the proposed system, with separate descriptions of the local reference implementation and the capabilities a deployed system would need.
- `IMPLEMENTATION.md`: a reproducible path from a deliberately failing Python example to worktree based changes, verification receipts, and session handoffs. It explains how to extract the reference `harness.py` from the masterplan.
- `TESTING.md`: a test procedure for the local reference, including negative cases for stale or changed evidence, altered files, unsafe paths, and interrupted work.
- `SECURITY.md`: the current security boundary, private reporting guidance, threat scenarios, and the controls required before running untrusted code or using sensitive credentials.
- `RESEARCH.md`: an evidence register that separates product documentation, published research, security standards, local observations, and engineering recommendations.

**Repository maintenance**

- `ROADMAP.md`: ordered implementation priorities, dependencies, acceptance gates, research milestones, and work that remains outside the local sample.
- `CONTRIBUTING.md`: contribution routes, reproducibility expectations, review criteria, security disclosure boundaries, and guidance for keeping technical claims attributable.
- `CHANGELOG.md`: a maintained record of reader visible changes and release decisions.

### Important limits of the initial material

The local reference example is an educational command line program. Its tests and receipts do not establish a secure execution sandbox, independently trusted build provenance, distributed task storage, or working integrations with every named coding agent. Those capabilities are described as future engineering work, not delivered functions. See [SECURITY.md](SECURITY.md), [ROADMAP.md](ROADMAP.md), and [TESTING.md](TESTING.md) for the boundaries and the evidence required to change that status.

## How release entries are written

A changelog entry should answer **what changed for the reader or developer**. A commit message often cannot answer that question on its own. For example, “refactor parser” says little; “reject a modified test receipt during audit” explains the observable effect.

Use these categories when they apply:

| Category | Include |
|---|---|
| Added | New documented capabilities, exercises, procedures, interfaces or files |
| Changed | Changes to existing behavior, contracts, instructions or supported environments |
| Deprecated | Supported behavior that is scheduled for removal, with an alternative where known |
| Removed | Features, interfaces or documented procedures no longer provided |
| Fixed | Corrections to reproducible defects or misleading instructions |
| Security | Released mitigations or material changes to a documented security boundary |

Do not create an empty category. Do not write an entry for every private experiment or every spelling correction. A typo that changes the meaning of a shell command, security warning, or test expectation deserves an entry. A routine punctuation fix generally does not.

### Evidence for an entry

Before an entry is marked released, the related pull request or maintainer note should identify:

1. The exact changed file, command, behavior, or reader facing claim.
2. The issue, test, or observation that justified the correction.
3. The revision carrying the change, along with reproducible test evidence where applicable.
4. Any compatibility effect, migration step, or remaining limitation.

Security entries should be coordinated with the process in [SECURITY.md](SECURITY.md). Do not publish unpatched exploit details or private reports as part of release notes.

## Creating the first release

There is no implied first release merely because this changelog exists. When the maintainer is satisfied that the chosen revision meets its publication checks:

1. Confirm that the repository contains the files listed under **Unreleased**. Remove entries for documents not actually included.
2. Run the procedures in [TESTING.md](TESTING.md) against the exact revision intended for release and retain the resulting evidence.
3. Check licensing, public claims, internal Markdown links, code listing consistency, and the disclosure route described in [SECURITY.md](SECURITY.md).
4. Select a versioning policy and create a real release tag. A `v0.x.y` format can distinguish experimental releases if the maintainer adopts that convention; no tag is prescribed by this document.
5. Move the applicable entries from **Unreleased** under the version heading with its actual release date. Record significant incompatibilities and known limitations, rather than treating publication as proof of completeness.
6. Publish the GitHub release from the tagged commit. Start a fresh **Unreleased** section for subsequent changes.

Use the form `## [version] - YYYY-MM-DD` once a release is real. Do not add a fabricated heading now to make the history look more established.

The project currently publishes a technical plan and educational reference, not a declared stable public software API. [Semantic Versioning](https://semver.org/) becomes particularly useful when compatibility promises are defined. Until then, document any changed command, file layout, schema, or recorded task format explicitly, even if the project uses an experimental `0.x` tag series.

## Keeping the record trustworthy

The maintainer should update **Unreleased** in the same pull request as a material reader visible change. During release review, compare those entries with the merged diff, completed issues, and actual test results. If a claimed feature was only documented but not implemented, say so; do not present a design as a shipped capability.

Retain previous released entries after subsequent revisions. Correct a historical error transparently instead of silently rewriting the significance of an older release. Links to tags and release comparisons can be added when the actual GitHub repository owner, release tags, and default branch are confirmed.

This format is informed by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [GitHub's release documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases). It is deliberately adapted for a repository containing both a technical masterplan and executable examples. The first job of the changelog is accuracy, not the appearance of a long release history.
