# Architecture and decisions

Author: Jason Stys. Scope: local evidence review for fictional spacecraft software, not hardware control.

The data flow is `bounded JSON → full schema/reference validation → latest-attempt graph evaluation → independent SQL verdict comparison → identity + inert export/UI`. A mismatch suppresses the entire report. The browser gets only finite authored scenarios; user-selected files are CLI-only. SQLite reference evaluation uses a transient in-memory database, distinct from optional disk history.

## Decisions

Python fits validation, deterministic graph traversal, standard-library packaging and test adapters. TypeScript provides strict UI contracts, readable DOM rendering and race-safe request handling. SQL provides a separately formulated relational implementation with window ranking and anti-joins, not just a place to save JSON. HTML/CSS provide native accessible controls, responsive tables and no external font/analytics dependencies.

An integrated local process is preferable to microservices here: no remote trust boundary, account service, container daemon or deployment credentials are needed. The cost is a local-only demo, no multi-user authorization and no concurrent collaboration. A real mission deployment would require signed evidence ingestion, approved trust policies, qualified workflows, access control and project-specific assurance review.

## Algorithm and tradeoffs

Index the highest attempt for each test; sort each test's history to check timestamp monotonicity. Any backwards clock step blocks that test even if its latest outcome passes. Link test verdicts to requirements and require all linked tests, plus at least one accepted test for each requirement/fault pair. Release-source equality gates overall readiness separately.

Let E be results, T tests, R requirements, F fault references and L links. The Python core uses O(E log E + T log T + R log R + R·F + requirement/fault coverage scans); it is **not advertised as globally linear**. Sorting/ranking avoids choosing results by file order. SQL deliberately uses correlated anti-joins and pairwise chronology checks; worst-case work can be quadratic in E and grow with linked requirements/faults. This slower independent checker is acceptable for bounded review packages, not streaming telemetry. Caps are 100 requirements, 200 tests, 100 faults, 1,000 results, 100 links per array and 1 MiB CLI JSON. `tools/benchmark.py` checks reviewed verdicts and reports informational time/traced allocation, not total RSS or a universal SLA.

All input collections are nonempty in schema 1. A requirement may have no linked test (reported blocked); a test may have no result (reported blocked), but entirely empty test/fault/result collections are invalid. This deliberate limitation simplifies a narrowly specified assurance package. There is no policy to waive critical or standard requirements.

## Sources and interpretation

[NASA SWE-052](https://swehb.nasa.gov/spaces/SWEHBVD/pages/102695427/SWE-052+-+Bidirectional+Traceability) and the [NASA systems-engineering handbook, crosscutting management](https://www.nasa.gov/reference/6-0-crosscutting-technical-management/) motivate explicit traceability and verification work products. They do not certify this implementation. Rules and demo scenarios are this project's own bounded educational interpretation. [GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations) and the [GitHub CLI verifier](https://cli.github.com/manual/gh_attestation_verify) inform the separately scoped delivery adapter. No NASA software, datasets or logos are copied.
