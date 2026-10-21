# Release procedure and rollback

Author: Jason Stys. Never publish a release from a failing, unreviewed or different commit.

1. Run lint/format, strict types, exact-line inventory, Python tests with branch-inclusive coverage ≥90%, six reviewed scenario contracts, real recorder JUnit capture/gate, Node tests/build/audit, three-browser accessibility/acceptance, and local frozen-app smoke. Audit the full locked dev graph; inspect secret/unrelated file exclusions.
2. Push reviewed source to `main`. Wait for **all eight Validation jobs** and **both CodeQL analyses** at that exact SHA; inspect job results and open CodeQL alerts separately. A workflow conclusion alone is not evidence that the app was used.
3. Dispatch `Portable release` with a new stable version. Preparation checks the latest successful Validation/CodeQL for exact `GITHUB_SHA`, then creates a new **draft** targeting that commit. Three OS jobs build and smoke their binaries, bundle applicable notices, produce ZIP/checksum pairs and upload directly to that draft. No public asset replacement, `--clobber`, Actions artifact upload or cache upload.
4. Verify draft target SHA and all six assets. Download every ZIP/checksum into a new private directory. Match GitHub digest, adjacent SHA-256, size, ZIP CRC, path confinement/no symlinks, expected assets/SQL/notices. Run only this freshly reviewed project's downloaded Windows app, smoke its exports/replay/history/HTTP and rerun all three browser suites against that **downloaded** app.
5. Write release notes with exact commit, actual hosted run URLs/job results, measured local test counts/coverage, bundle hashes and limitations. Publish the draft only after all gates pass. Verify public release and tag SHA. Keep the source checkout clean.

Draft upload failure: leave the draft unpublished, fix source and produce a new reviewed version; do not overwrite an already public asset. A runtime regression: advise users to stop the affected local process and use a previously reviewed release if available, otherwise use source only after validation. Preserve private user exports/history. There is no remote deployment, data migration, background updater, feature flag or infrastructure rollback. Do not delete user data or old runs as a release step.

Unsigned desktop targets tested by CI: Windows x64, Ubuntu/Linux x64 and macOS ARM64. Other versions/architectures need their own build and test. No signing/notarization or mobile installation claim. Respect OS protection policies.
