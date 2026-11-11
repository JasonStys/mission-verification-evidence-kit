# Installed Windows application validation — 10 November 2026

By Jason Stys. The published **1.1.0** application was installed and
used with isolated synthetic inputs; runtime source: `2743307a90da1621392fcafa138b6e103db751d5`.
This edition supplements the earlier project/validation documents. It does not
replace their hashes, workbook evidence or historical provenance.

## Observed behavior

Exact public release, provider/sidecar hashes and installed resources verified; installed bytes unchanged.

The existing packaged CLI/API and native feature acceptance helper passed on the installed executable.

SQL and core results agreed; provenance_authenticated remained false. Failed, stale and missing baseline reasons retained separate source and expiry bindings.

Actual compiled-application browser journey passed. Both images were individually inspected; cleanup left no owned child process.

## Documentation and operation

Every page of the [four-page illustrated guide](windows-application-guide.docx)
was individually inspected and its OOXML schema validated. The paired screenshots
come from the actual compiled application. Source excerpts identify the immutable
runtime revision and exact source lines. The [review manifest](windows-application-guide.json)
records document, screenshot and rendered-page digests.

Use the complete checksummed portable distribution from Releases. The launch
command is `serve --port 0`; normal launch opens the app's browser interface.
Return to its own console and press Ctrl+C to stop the service. Browser-tab close
alone does not stop it. Individual Desktop/Start-menu links were created and
their exact targets, arguments and installed file hashes verified separately;
that metadata check is not a claim that normal default-browser activation was
exercised in the native acceptance above.

Prepared inputs are part of the full project workflow, not a separate demo app.
No existing account/profile, installation file or Docker setting was changed by
these checks. Public hosting, signed installers, mobile installation, real
hardware and operational certification remain outside this evidence.

## Project-specific boundaries

Declared evidence consistency, not certification, authenticated provenance or proof omitted requirements are complete.

This commit changes documentation integration only. New hosted runs must pass for
the new documentation commit; earlier runtime results do not certify future code.
