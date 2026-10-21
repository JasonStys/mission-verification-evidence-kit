# Input schema, API and gate semantics

Author: Jason Stys. Canonical editable example: `examples/recorder.json`. Unknown fields, duplicate keys/IDs/attempts, non-finite numbers, booleans as integers, invalid digests, unknown links and control characters in titles are rejected. Inputs are copied; callers cannot mutate a previously validated graph through aliases.

## Schema 1

- Root: `schema:1`, `title`, `source` (40 lowercase hex), `as_of` (Unix seconds 1–4102444800), `max_age` (seconds 1–31536000), `requirements`, `tests`, `faults`, `results`, `release`.
- Requirement: `id`, `title`, `revision` (1–10000), `criticality` (`critical` or `standard`).
- Test: `id`, `title`, `requirements` (nonempty ID array), `faults` (possibly empty), `definition` (64 lowercase hex).
- Fault: `id`, `title`, `requirements` (nonempty). A linked test and fault must share a requirement; coverage is evaluated per actual common requirement, not globally.
- Result: `id`, `test`, `attempt` (1–1000000), `completed` (same epoch bounds), `source`, `definition`, `baselines` (exactly the test's requirement IDs with their revisions), `status` (`pass`, `fail`, `error`, `skipped`), `artifact` (declared 64-hex digest).
- Release: `source`, `artifact` (declared 64-hex digest). The kit compares its source but does not fetch/hash a corresponding binary or claim its authentication.

IDs match `[A-Z][A-Z0-9-]{0,39}`; titles are 1–160 codepoints without characters below U+0020. Collections are bounded/nonempty as described in architecture. Result artifact and test-definition hashes in authored fixtures are explicitly synthetic. They are not measured artifacts. The actual JUnit adapter computes the JUnit bytes' digest and accepts a caller-supplied definition/source binding.

## Acceptance

Choose largest attempt **for each test**, regardless of file order. Accept only pass + exact candidate source + exact definition + all current linked requirement revisions + age in inclusive `[0,max_age]` + monotonic history times by attempt. Never fall back to an older acceptable result. Reasons include `missing-result`, `fail`, `skipped`, `error`, `source-mismatch`, `definition-mismatch`, `baseline-mismatch`, `future-result`, `expired`, `chronology-conflict`.

A requirement is verified only if it has tests, **every** linked test is accepted and every declared linked fault has an accepted test covering that same requirement/fault pair. Matrix reasons: `missing-test`, `unaccepted-test`, `fault-gap`. Overall `ready` also requires matching release source. Both criticality labels use identical strict gates; labels aid human prioritization, not waivers. No links are inferred from title keywords.

Reports contain all original input/attempts, sorted requirement/test rows, specific blockers, counts, SQL agreement and explicit `provenance_authenticated:false`. `id` is SHA-256 of finite sorted compact JSON plus newline with `id` omitted. Changing input order can change identity even when verdicts are equal: identity means exact package content, not semantic equivalence.

## HTTP

Only `http://127.0.0.1:<port>`; exact Host and same/absent Origin. GET `/api/health`, `/api/catalog`, `/api/run?scenario=complete&max_age=86400`, `/api/report?scenario=complete&max_age=86400&format=json`. Report formats: `json`, `csv`, `html`, `input`. Catalog supplies six scenarios and finite age choices 3600/86400/604800 seconds. Unknown/duplicate/unsupported parameters: 400; foreign origin: 403; unapproved paths: 404; mutating methods: 405; target over 1024 characters: 414; internal resource/checker failure: generic 500. API `/run` does not accept `format`. No upload, source-file route, shell or arbitrary URL fetch exists.

## JUnit subset

`python -m tools.capture_demo` runs only `tests/test_recorder_demo.py`, captures real JUnit and gates it. The generic invocation is `python -m tools.collect_evidence --junit <path> --source <40hex> --definition <64hex> --completed <epoch> --output <new-path>`, then `python -m evidencekit gate --input <new-path>`.

Only UTF-8 `testsuite`/`testsuites`, exactly one of each `test_recorder_roundtrip`, `test_recorder_reset`, `test_recorder_invalid`. Unknown/duplicate/missing cases, unsupported case elements, conflicting outcomes, contradictory aggregate counts, suite-level unmapped failures, DTD/entities, NUL, invalid XML/UTF-8 and oversize files are rejected. Child outcome elements determine status; optional aggregate counts must agree. This is a fixed demonstration adapter, **not every JUnit dialect**. Source SHA, completed time and definition digest are caller declarations, not cryptographic proof. No XML contents are executed.
