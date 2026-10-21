# Mission Verification Evidence Kit

[![Validation](https://github.com/JasonStys/mission-verification-evidence-kit/actions/workflows/validate.yml/badge.svg)](https://github.com/JasonStys/mission-verification-evidence-kit/actions/workflows/validate.yml)
[![CodeQL](https://github.com/JasonStys/mission-verification-evidence-kit/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/mission-verification-evidence-kit/actions/workflows/codeql.yml)

**Created by Jason Stys** · [Portfolio / contact](https://github.com/JasonStys) · [Download portable apps](https://github.com/JasonStys/mission-verification-evidence-kit/releases/latest)

A local systems-assurance workbench that connects fictional spacecraft requirements to test procedures, fault scenarios, attempt history and release metadata. It makes missing and stale evidence visible instead of reducing readiness to a green test-count badge.

Python evaluates the graph; **independent SQL** checks every requirement verdict. A strict TypeScript interface shows the matrix, blockers, latest evidence and replayable exports. No cloud account, external AI, database service or telemetry is needed.

## What it demonstrates

- Bidirectional requirement ↔ test ↔ fault links, including orphan/unknown-link rejection.
- Latest-attempt selection: newer failures, errors and skipped tests cannot be hidden by older passes.
- Source, requirement revision, test-definition, freshness and clock-order checks.
- Every linked test must be accepted; every declared fault obligation needs accepted coverage.
- Deterministic JSON content identities, CSV with formula neutralization, escaped HTML, replay inputs and optional immutable SQLite history.
- A bounded adapter from **actual JUnit** for three reviewed recorder tests; CI runs those tests, imports their results and gates the resulting matrix.
- Reuse of [secure-delivery-pipeline-lab](https://github.com/JasonStys/secure-delivery-pipeline-lab): independently selected signer/source identity, real GitHub attestation verification, and no payload execution.
- Six deliberate scenarios, property-based/differential tests, security boundaries, three-browser accessibility checks, and smoke-tested Windows/Linux/macOS bundles.

“Verified” means that **declared evidence satisfies this kit’s rules**. It does not prove that arbitrary supplied results are truthful, complete or authentic. Content hashes are not signatures. The delivery verifier authenticates a separate existing demo release, not the mission fixtures. This is civilian educational software, **not flight qualification, mission authorization, or safety certification**.

## Use the portable app

Download the ZIP matching your OS/architecture and its `.sha256` from Releases. Verify its digest, extract **the entire archive**, then launch `MissionVerificationEvidenceKit` (`.exe` on Windows). A loopback-only browser UI opens automatically; close its console to stop it. No Python, Node, IDE, installer, elevation or background service is required.

The binaries are **unsigned**, not mobile apps or universal installers. Do not bypass OS security warnings or policy. CI tests Windows x64, Linux x64 and macOS ARM64; compatibility with other systems is not promised. See [user guide](docs/USER_GUIDE.md), [release procedure](docs/RELEASE.md), and [third-party notices](docs/THIRD_PARTY.md).

## Run from source

Python 3.12–3.14; Node 24. Commands below use `python`; on Windows activate the environment with `.venv\Scripts\Activate.ps1`, or invoke `.venv\Scripts\python.exe` directly. Other platforms use `.venv/bin/python`.

```sh
python -m venv .venv
# Activate the environment using your platform's normal method.
python -m pip install --require-hashes -r requirements-dev.lock
npm ci
npm run build
python -m evidencekit serve
```

Runtime Python uses the standard library only; the locked packages are development/test/build tools. No Docker is required.

```sh
python -m evidencekit export --scenario regression --format html --output regression.html
python -m evidencekit export --input examples/recorder.json --output evidence.json --history private-history.sqlite3
python -m evidencekit gate --input examples/recorder.json
```

`gate` exits 0 for ready, 2 for blocked, 1 for invalid/unavailable evidence. Exports are create-only; history is local, unencrypted, capped at 100 unique reports and never auto-pruned. Do not place sensitive inputs or histories in Git.

## Validate

```sh
python -m ruff check evidencekit tests tools launcher.py
python -m ruff format --check evidencekit tests tools launcher.py
python -m mypy evidencekit
python tools/verify_repo.py
python -m pytest --cov=evidencekit --cov-report=term-missing
python -m tools.benchmark
python -m tools.capture_demo
npm run format:check
npm test
npm run build
npm run audit
npx playwright install chromium firefox webkit
npm run test:e2e
python tools/package_app.py
```

`capture_demo` requires a committed checkout, creates a **new** ignored `.runtime/ci-evidence` folder and will not overwrite an earlier capture. Linux Playwright may require `npx playwright install --with-deps`. CI independently runs four Python platform/version combinations, three browser engines, three portable builds and two CodeQL language analyses. Workflows do **not** upload Actions artifacts or caches. Actual final hosted run IDs, target commit and release checksums are recorded in release notes; [validation report](docs/VALIDATION.md) explains the gates and local results.

## Repository map

| Path                                   | Responsibility                                                                          |
| -------------------------------------- | --------------------------------------------------------------------------------------- |
| `evidencekit/model.py`                 | Strict graph schema, finite settings and synthetic scenarios                            |
| `evidencekit/engine.py`                | Latest attempts, blockers, requirement matrix, SQL cross-check and content ID           |
| `evidencekit/resources/verify.sql`     | Independently formulated relational verdicts                                            |
| `evidencekit/junit.py`                 | Bounded, fixed-suite JUnit adapter                                                      |
| `evidencekit/delivery/`                | Reviewed reusable integrity/provenance verification; no payload execution               |
| `evidencekit/reports.py`               | Inert exports and optional private immutable history                                    |
| `evidencekit/server.py`, `__main__.py` | Read-only loopback website, CLI exports/gate/delivery verification                      |
| `web/`                                 | Accessible responsive TypeScript/CSS/HTML workbench                                     |
| `tests/`                               | Unit, property, adversarial, real recorder, HTTP and three-browser acceptance tests     |
| `tools/`                               | Evidence capture, reviewed benchmark contracts, inventories and gated release packaging |
| `examples/`, `docs/`, `licenses/`      | Editable synthetic input, complete documentation/evidence and notices                   |

The [file catalog](docs/FILE_CATALOG.md) summarizes **every file**. The generated [exact-line code index](docs/CODE_INDEX.md) lists functions, classes, arguments, assigned variables and structural identifiers; source headers describe responsibilities and link to that maintained index instead of duplicating fragile line numbers.

Start with [user guide](docs/USER_GUIDE.md), [schema/API](docs/SCHEMA.md), [architecture](docs/ARCHITECTURE.md), [security](SECURITY.md), [validation](docs/VALIDATION.md), [provenance integration](docs/PROVENANCE.md), and [limitations](docs/LIMITATIONS.md).
