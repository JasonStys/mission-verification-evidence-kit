# Portable release refresh validation — 2026-11-09

By Jason Stys. Version 1.1.0 prepares metadata-bound human revalidation queues, exact freshness deadlines and structural evidence gaps.

## Recorded checks

Windows/Python3.14.6:266 Python tests passed with98.13% combined coverage (unchanged90% gate),4 TypeScript tests and39 real source Chromium/Firefox/WebKit journeys passed. Ruff, strict mypy and production build passed; all6 existing summary benchmark contracts remain unchanged. The real packaged queue prioritizes a failed critical TEST-STORE, preserves source/revision metadata, verifies the independent first-invalid1800084601 deadline and missing-procedure case, then downloads JSON equal to the frozen API. All previous notices, fourformats, immutableSQLhistory and replay checks are retained.

The actual Windows archive was inspected and extracted into a fresh temporary directory. Its executable ran from an unrelated working directory, preserved every previous native smoke contract, served only its owned loopback URL, matched package/version/instance identity, delivered actual compiled assets and completed the new real Chromium workflow/export. Local archive SHA-256: `c692bd2f361230bfb84a10a3fa01ee6f9799e74b37301a9bb35eacc9f7972c0d`. This development archive honestly records dirty-source metadata; it is local acceptance evidence rather than a published clean-source release.

The original seventy release/archive/runtime tests use independent GitHub metadata fixtures and actual small archive bytes. They reject wrong source/version/repository, running/failed/incomplete/ambiguous workflow histories, existing draft/tag/public release, asset/checksum/metadata mismatch, link/path escape and corrupt frozen identity. Release guards remain active under optimized Python. No GitHub writes occur in these tests. Existing coverage, native/oracle, security and browser gates remain unchanged.

## Reproduce and limits

Use exact development locks and target native toolchains. Run the repository's full coverage suite, deterministic benchmark, strict lint/types/index/format checks, TypeScript tests/build and three-engine source browser suite, then `python tools/package_app.py`. The last command launches the real extracted application and its new feature in Chromium; it needs Node/Playwright only as build-time acceptance tools. Ordinary users need neither Python nor Node.

Declared synthetic evidence only: SQL agreement checks consistency, not authenticity, completeness of omitted requirements, real test execution or flight qualification. The queue schedules human review and cannot waive a gate.

Local native acceptance covers Windows only. Linux/macOS executable, links, ABI and UI still require real native CI. These unsigned portable folders are not installers or clean-machine installation proof. Native tests bypass the default OS browser opener, whose frozen POSIX inherited-library behavior remains a manual desktop check. No accounts, previous releases or user histories are changed. No push, dispatch, tag or release mutation was performed by this local work. The coordinator must review clean exact-source main checks, all three native jobs and all six uploaded assets/checksum digests before publishing.

## Authenticated draft lookup correction

The hosted application/UI checks passed before upload exposed an API-contract error: GitHub's releases-by-tag endpoint returns published releases and can return404 for an untagged draft. Preparation and upload now use a complete authenticated release listing (100 entries per page, at most three pages), require a unique exact tag and reread its numeric release ID. They validate list/detail identity and same-repository API/upload/assets URLs; upload additionally requires the exact source and non-prerelease draft state. A full cap, duplicated or swapped identity, lost access, malformed metadata,404 or network error cannot authorize absence or a write.

All19 independent real-shape API contract tests pass in the complete recorded suite. Existing archive/checksum/source/collision/non-clobber guards remain active; no application acceptance, coverage, security or native-OS job was removed or skipped. The previous actual extracted Windows workflow and separate three-engine source journeys remain recorded above; this follow-up changes release metadata acquisition, not the application feature or its numerical kernel. No live upload, draft mutation, push or workflow dispatch was performed by this local correction.
