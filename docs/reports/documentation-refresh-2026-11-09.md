# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `2743307a90da1621392fcafa138b6e103db751d5`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File                                                 | Bytes | SHA-256                                                            | Reviewed scope                                                                                                                      |
| ---------------------------------------------------- | ----: | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| [project-guide.docx](project-guide.docx)             | 43160 | `65699c69e4e0ec36ab5d8a05949be4c145d02cb17ecb0b27171f7397328cb4dc` | 4 pages, each viewed individually                                                                                                   |
| [validation-review.docx](validation-review.docx)     | 41986 | `d493b5e2078d2113db685c545486a657621c9dd3d5637e9c538b0f97474e72c2` | 3 pages, each viewed individually                                                                                                   |
| [validation-evidence.xlsx](validation-evidence.xlsx) |  7465 | `5acef53e65fea7bae3d870d1858aee02319e3aa9c501950904fad0282b8da028` | Both tab previews; two actual Excel Tables/autoFilters; four formulas; failure-change/restore recalculation and zero formula errors |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval. Workbook review inspected both tab previews and actual exported Table/autoFilter elements; recalculated success/failure summaries were compared independently with workflow metadata. Static previews do not draw Excel dropdown arrows; the exported workbook contains the actual filters.

## Evidence and change boundary

- Functional baseline: `2743307a90da1621392fcafa138b6e103db751d5`.
- Workflow observation: `2026-11-10T05:25:40.628667+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. The Excel source inventory is not a per-test execution report. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.

## Integration-local checks

Observed at `2026-11-10T07:48:34.626819+00:00` on Windows with this repository’s existing development tools. Python commands use its isolated development environment. The documentation source baseline remains the immutable revision above; these checks validate this documentation integration locally.

| Command                                                             | Observed result |
| ------------------------------------------------------------------- | --------------- |
| `python tools/verify_repo.py --write`                               | Passed, exit 0. |
| `python tools/verify_repo.py`                                       | Passed, exit 0. |
| `python -m ruff check evidencekit tests tools launcher.py`          | Passed, exit 0. |
| `python -m ruff format --check evidencekit tests tools launcher.py` | Passed, exit 0. |
| `python -m mypy evidencekit`                                        | Passed, exit 0. |
| `python -m pytest --cov=evidencekit --cov-report=term-missing`      | Passed, exit 0. |
| `node node_modules/prettier/bin/prettier.cjs --check .`             | Passed, exit 0. |
| `node node_modules/vitest/vitest.mjs run`                           | Passed, exit 0. |

The independent publication audit also matched every copied Office file to its approved SHA-256, checked ZIP package integrity and current page/tab approvals, compared immutable workflow/source metadata, and resolved every local handbook/report link within the repository. Hosted PR/main, browser, platform and container jobs remain separate required checks; they are not inferred from these local results.

The existing suite passed 266 Python tests at 98.13% combined coverage (90% floor retained) and 4 TypeScript tests. The first sandboxed attempt could not connect to the test-owned localhost listeners (Windows error 10013); the complete unchanged suites passed with narrowly scoped execution access. No user service was adopted or modified, no coverage floor was reduced, and no runtime implementation changed.
