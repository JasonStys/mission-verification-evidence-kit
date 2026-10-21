# Validation plan and measured results

Author: Jason Stys. Reports describe observed checks; they do not confer certification. Final exact-SHA hosted run IDs, portable digests and downloaded-app acceptance are recorded in [release notes](https://github.com/JasonStys/mission-verification-evidence-kit/releases/latest) to avoid a self-referential report-only commit invalidating the release SHA.

## Layers

| Layer                   | Actual assertion                                                                                                                                                 |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Schema/security         | Types/bounds, duplicate/unknown references and attempts, malformed JSON/XML, regular files, ZIP paths, identity policies, no secret/source routes                |
| Traceability            | Six reviewed scenarios plus each failure reason, all-test obligations, per-requirement fault coverage, missing/latest/clock/revision semantics                   |
| Differential/properties | Python versus independently formulated SQL, randomized age/status and permutations of collection order                                                           |
| Real execution adapter  | Three real synthetic recorder tests → JUnit bytes → strict import → independent matrix → gate exit                                                               |
| Reports/history         | Four formats, replay equality, HTML escaping/CSV formula defense, identity checks, immutable/idempotent bounded SQLite records                                   |
| Local HTTP              | Real server requests, exact origins/Host, no mutating routes, restrictive headers, finite queries and generic failures                                           |
| Browser                 | Chromium/Firefox/WebKit: six cases, filtering, stale control invalidation, failed/delayed requests, actual downloads, narrow-screen containment, axe WCAG checks |
| Delivery                | Authored adversarial unit tests use fakes explicitly; separate live CLI verifies existing signed v1.0.1 manifest/all assets, without payload execution           |
| Packaging               | Actual frozen app on three hosted OS targets; exports/replay/history/notices/loopback HTTP smoke; then downloaded Windows binary + full browser rerun            |

Python branch-inclusive coverage is gated at 90%, not just statement coverage. Hypothesis uses a deterministic 100-example profile with deadline disabled; numerical timing is not correctness. No test is deliberately skipped to obtain a green release. Browser retries are zero; traces/videos/screenshots are off for routine CI to avoid storage uploads.

## Local observations

Final local suite: 174 Python tests passed, 97.98% branch-inclusive coverage on Python 3.14.6, four TypeScript helper tests passed, all 36 Chromium/Firefox/WebKit checks passed, production assets built, full locked Python dependency audit and npm audit found no known vulnerabilities. The Windows frozen app passed all exports/replay/history/notices/HTTP smoke checks. Three real recorder tests were also captured to JUnit, imported and passed through the independent evidence gate. Actual live four-asset delivery attestation verification passed for existing demo v1.0.1 commit `6e6dc95ce47d4f7dfdf019ccd84db8bdd83f8828`; no downloaded delivery payload was run. Final hosted and downloaded-release acceptance results are in release notes.

Initial browser validation found two project issues: a matrix container's implicit minimum width overflowed a phone viewport, and a label's computed accessible name did not match the intended filter name. Fixed with an explicit shrinkable grid child and explicit accessible label; the browser suite retains regression checks. A restricted Windows Firefox process launch was an environment failure, not evidence of an application defect. Reruns use normal OS permissions, not disabled browser sandbox/security. Release is withheld until final full reruns and hosted jobs pass.

`docs/reports/benchmark.json` contains reviewed deterministic summaries, checked on every model matrix job. `tools/benchmark.py` prints elapsed time and Python traced peak allocation (not process RSS), without universal speed claims. Exact-line and file inventories are generated after formatting and checked for drift. No Actions cache/artifact upload is configured. Storage/billing information is private account metadata, not included in public validation reports.
