# Reused delivery verifier and provenance distinction

Author: Jason Stys. The project deliberately separates **declared mission evidence**, **content integrity**, and **authenticated release origin**.

`evidencekit/delivery/io.py` and `verify.py` are adapted from Jason Stys's MIT-licensed `secure-delivery-pipeline-lab` source snapshot `c596acb9989c205c8697d9575141be9111b922d4` (import paths/header index changed; no payload promotion code is copied). The original MIT notice is retained as `licenses/SECURE_DELIVERY.txt` and included in portable bundles. Authored adversarial boundary tests are reused/adapted with new isolated inert fixtures. No upstream release payload is executed.

The `verify-delivery` command accepts the original project's **exact four-file** release shape: `release.json`, `release-probe-VERSION.pyz`, `sbom.cdx.json`, `validation.json`. It checks independent repository/version/full-SHA/workflow policy, file names/types/sizes, checksums, and ZIP member confinement. Then it requires real `gh attestation verify` on the manifest **and all three assets**, with repo, signer workflow/digest, source digest/ref, GitHub hostname, SLSA provenance type and denial of self-hosted builders. Missing CLI, network/verification errors, wrong identities or tampering fail closed. Hash-only preflight is never authentication.

Reproduce the live integration without executing the payload:

```sh
gh release download v1.0.1 --repo JasonStys/secure-delivery-pipeline-lab --dir private-delivery --pattern release.json --pattern release-probe-1.0.1.pyz --pattern sbom.cdx.json --pattern validation.json
python -m evidencekit verify-delivery --directory private-delivery --commit 6e6dc95ce47d4f7dfdf019ccd84db8bdd83f8828 --version 1.0.1 --output private-receipt.json
```

The listed SHA was independently obtained from the existing public release tag for this reviewed integration. Re-establish trust before adopting a different release. A new receipt is create-only and records the selected policy and authenticated manifest, not credentials. It is not an immutable signed receipt itself; a copied/edited receipt cannot authenticate another package. Nothing in the browser or mission readiness logic trusts such a receipt. This kit's portable ZIP checksums likewise provide integrity, **not signing/notarization**. A future signed mission-evidence ingestion format needs its own trust model; the existing narrow demo manifest is not silently generalized.

Primary reference: [GitHub CLI attestation verify](https://cli.github.com/manual/gh_attestation_verify), [GitHub attestations overview](https://docs.github.com/en/actions/concepts/security/artifact-attestations).
