"""Deterministic graph evaluation plus independent SQL cross-check by Jason Stys.

Functions analyze/build_run; variables latest, links, reasons, rows and report identity.
Definitions/parameter lines: docs/CODE_INDEX.md. Hashes identify content, not its author.
"""

import hashlib
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from typing import Any

from evidencekit.delivery.io import canonical
from evidencekit.model import Settings, fixture, validate

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))


def sql_reference(value: dict[str, Any]) -> list[dict[str, Any]]:
    """Independently evaluate relational traceability using JSON1 and reviewed window/anti-join SQL."""
    query = (ROOT / "evidencekit/resources/verify.sql").read_text(encoding="utf-8")
    with closing(sqlite3.connect(":memory:")) as db:
        db.row_factory = sqlite3.Row
        return [dict(row) for row in db.execute(query, {"document": canonical(value).decode()})]


def analyze(document: dict[str, Any]) -> dict[str, Any]:
    """Use latest attempt per test; require every linked test and every fault obligation, with no waivers."""
    value = validate(document)
    latest: dict[str, Any] = {}
    chronology: dict[str, list[tuple[int, int]]] = {}
    for result in value["results"]:
        key = result["test"]
        chronology.setdefault(key, []).append((result["attempt"], result["completed"]))
        if key not in latest or result["attempt"] > latest[key]["attempt"]:
            latest[key] = result
    backwards = {
        key
        for key, times in chronology.items()
        if any(a[1] > b[1] for a, b in zip(sorted(times), sorted(times)[1:], strict=False))
    }
    test_rows = []
    linked: dict[str, list[dict[str, Any]]] = {r["id"]: [] for r in value["requirements"]}
    revisions = {r["id"]: r["revision"] for r in value["requirements"]}
    for test in sorted(value["tests"], key=lambda t: t["id"]):
        result = latest.get(test["id"])
        reasons = []
        if result is None:
            reasons.append("missing-result")
        else:
            if result["status"] != "pass":
                reasons.append(result["status"])
            if result["source"] != value["source"]:
                reasons.append("source-mismatch")
            if result["definition"] != test["definition"]:
                reasons.append("definition-mismatch")
            if any(result["baselines"][r] != revisions[r] for r in test["requirements"]):
                reasons.append("baseline-mismatch")
            age = value["as_of"] - result["completed"]
            if age < 0:
                reasons.append("future-result")
            elif age > value["max_age"]:
                reasons.append("expired")
            if test["id"] in backwards:
                reasons.append("chronology-conflict")
        row = {
            "id": test["id"],
            "title": test["title"],
            "requirements": sorted(test["requirements"]),
            "faults": sorted(test["faults"]),
            "result": result,
            "reasons": sorted(reasons),
            "accepted": not reasons,
        }
        test_rows.append(row)
        for req in test["requirements"]:
            linked[req].append(row)
    rows = []
    for req in sorted(value["requirements"], key=lambda r: r["id"]):
        tests = linked[req["id"]]
        faults = [f for f in value["faults"] if req["id"] in f["requirements"]]
        uncovered = [
            f["id"]
            for f in faults
            if not any(t["accepted"] and f["id"] in t["faults"] for t in tests)
        ]
        reasons = []
        if not tests:
            reasons.append("missing-test")
        if any(not t["accepted"] for t in tests):
            reasons.append("unaccepted-test")
        if uncovered:
            reasons.append("fault-gap")
        rows.append(
            {
                **req,
                "tests": [t["id"] for t in tests],
                "faults": sorted(f["id"] for f in faults),
                "uncovered_faults": sorted(uncovered),
                "reasons": sorted(reasons),
                "status": "blocked" if reasons else "verified",
            }
        )
    reference = sql_reference(value)
    expected = [{"id": row["id"], "verified": int(row["status"] == "verified")} for row in rows]
    if reference != expected:
        raise RuntimeError("Independent SQL verification disagrees; no evidence is emitted")
    release_match = value["release"]["source"] == value["source"]
    report = {
        "schema": 1,
        "input": value,
        "requirements": rows,
        "tests": test_rows,
        "summary": {
            "total": len(rows),
            "verified": sum(r["status"] == "verified" for r in rows),
            "blocked": sum(r["status"] == "blocked" for r in rows),
            "accepted_tests": sum(t["accepted"] for t in test_rows),
            "release_source_matches": release_match,
            "ready": release_match and all(r["status"] == "verified" for r in rows),
        },
        "verification": {
            "sql_agrees": True,
            "provenance_authenticated": False,
            "scope": "Declared synthetic evidence only; no flight qualification",
        },
    }
    report["id"] = hashlib.sha256(canonical(report)).hexdigest()
    return report


def build_run(settings: Settings) -> dict[str, Any]:
    """Evaluate a finite educational fixture without external files, network or processes."""
    return analyze(fixture(settings))
