# Mission Verification Evidence Kit handbook

By Jason Stys.

Connect fictional mission requirements to test procedures, fault obligations and release evidence. Review missing, stale or mismatched evidence through independent Python and SQL verdicts before planning revalidation; declared evidence is not flight qualification.

The released 1.1.0 portable evidence kit includes metadata-bound revalidation queues: prioritize blocked critical tests, see exact freshness deadlines, identify missing procedures and preserve the source and baseline revisions needed for review.

The original requirement/test/fault traceability, SQL cross-check, export formats and immutable local history are retained. The extracted app verifies a failed critical test, an independently calculated first-invalid timestamp, missing-procedure guidance and an exact JSON download. It turns declared evidence gaps into a practical human review queue without waiving gates or pretending to execute tests.

## Read the documentation

The [illustrated Windows guide](reports/windows-application-guide.docx) adds actual
installed-app screenshots, a worked scenario, source excerpts and dated acceptance.
Its [review manifest](reports/windows-application-guide.json) identifies the exact
reviewed bytes. Earlier Office editions below retain their historical baselines.

| Edition                                                      | Audience and contents                                                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [project-guide.docx](reports/project-guide.docx)             | User and developer guide: purpose, current usage, design, boundaries and source references.                        |
| [validation-review.docx](reports/validation-review.docx)     | Reviewer edition: exact tested baseline, observed workflows, dated local results and remaining limits.             |
| [validation-evidence.xlsx](reports/validation-evidence.xlsx) | Two filterable Excel Tables for observed workflows and test-source inventory, with recalculating outcome formulas. |

The editable Markdown remains the maintenance source. The Word files are readable editions. The workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [RELEASE](RELEASE.md)
- [USER GUIDE](USER_GUIDE.md)
- [releases/v1.1.0](releases/v1.1.0.md)

### Design and contracts

- [ARCHITECTURE](ARCHITECTURE.md)

### Security and validation

- [REVALIDATION QUEUE](REVALIDATION_QUEUE.md)
- [VALIDATION](VALIDATION.md)

## Historical results and reproduction

The reviewed source is [`2743307a90da1621392fcafa138b6e103db751d5`](https://github.com/JasonStys/mission-verification-evidence-kit/tree/2743307a90da1621392fcafa138b6e103db751d5). The observed functional workflow baseline is `2743307a90da1621392fcafa138b6e103db751d5`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/PORTABLE_REFRESH_20261109.md)
- [Current Actions](https://github.com/JasonStys/mission-verification-evidence-kit/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Declared synthetic evidence consistency only; SQL agreement does not authenticate provenance or reveal omitted requirements.
- The queue plans human review; it does not execute tests, waive release gates or establish flight qualification.
- Unsigned desktop portable folders, not system installers or clean-machine proof. Three-OS extracted-native checks drive an owned URL; default OS browser opening remains manual.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.
