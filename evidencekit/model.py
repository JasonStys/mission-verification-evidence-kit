"""Strict bounded traceability input and synthetic fixtures by Jason Stys.

Functions validate, load_input, fixture; Settings selects finite UI cases and freshness policy.
Variables: CASES, CHOICES, SHA, NOW; exact declarations/parameters: docs/CODE_INDEX.md.
No evidence is executed and no SHA-256 claim implies authenticated provenance.
"""

import copy
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evidencekit.delivery.io import load_json

SHA = "a" * 40
NOW = 1800000000
CASES = {
    "complete": "Complete baseline",
    "missing": "Unverified requirement",
    "stale": "Changed requirement revision",
    "regression": "Newer failing attempt",
    "fault-gap": "Missing fault coverage",
    "mixed": "Mixed evidence problems",
}
CHOICES = {"max_age": (3600, 86400, 604800)}


@dataclass(frozen=True)
class Settings:
    """Finite browser parameters: scenario is a fixture key, max_age is seconds inclusive."""

    scenario: str = "complete"
    max_age: int = 86400

    def __post_init__(self) -> None:
        """Reject unsupported settings including booleans masquerading as integers."""
        if (
            not isinstance(self.scenario, str)
            or self.scenario not in CASES
            or type(self.max_age) is not int
            or self.max_age not in CHOICES["max_age"]
        ):
            raise ValueError("Unsupported settings")


def fields(value: Any, expected: set[str]) -> None:
    """Require an object with precisely the declared keys; never silently discard input."""
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("Unexpected object fields")


def text(value: Any, pattern: str = r"[A-Z][A-Z0-9-]{0,39}") -> None:
    """Check bounded identifiers or caller-selected fixed digest patterns."""
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        raise ValueError("Invalid identifier or digest")


def integer(value: Any, low: int, high: int) -> None:
    """Require exact bounded integers, excluding bool and floating-point coercion."""
    if type(value) is not int or not low <= value <= high:
        raise ValueError("Invalid integer")


def title(value: Any) -> None:
    """Allow human descriptions without control characters, at most 160 codepoints."""
    if not isinstance(value, str) or not 1 <= len(value) <= 160 or any(ord(c) < 32 for c in value):
        raise ValueError("Invalid title")


def links(value: Any, allowed: set[str], minimum: int = 0) -> None:
    """Require unique declared references; order has no semantic effect."""
    if not isinstance(value, list) or len(value) < minimum or len(value) > 100:
        raise ValueError("Invalid links")
    for item in value:
        text(item)
    if len(set(value)) != len(value) or set(value) - allowed:
        raise ValueError("Unknown or repeated link")


def records(value: Any, maximum: int) -> set[str]:
    """Bound a nonempty record collection and require globally unique local IDs."""
    if not isinstance(value, list) or not 1 <= len(value) <= maximum:
        raise ValueError("Invalid record count")
    ids = set()
    for row in value:
        if not isinstance(row, dict):
            raise ValueError("Record is not an object")
        text(row.get("id"))
        if row["id"] in ids:
            raise ValueError("Duplicate record ID")
        ids.add(row["id"])
    return ids


def validate(value: Any) -> dict[str, Any]:
    """Validate and copy the complete revisioned graph; malformed input never becomes a green matrix."""
    fields(
        value,
        {
            "schema",
            "title",
            "source",
            "as_of",
            "max_age",
            "requirements",
            "tests",
            "faults",
            "results",
            "release",
        },
    )
    integer(value["schema"], 1, 1)
    title(value["title"])
    text(value["source"], r"[a-f0-9]{40}")
    integer(value["as_of"], 1, 4102444800)
    integer(value["max_age"], 1, 31536000)
    reqs = records(value["requirements"], 100)
    tests = records(value["tests"], 200)
    faults = records(value["faults"], 100)
    records(value["results"], 1000)
    for row in value["requirements"]:
        fields(row, {"id", "title", "revision", "criticality"})
        title(row["title"])
        integer(row["revision"], 1, 10000)
        if row["criticality"] not in ("standard", "critical"):
            raise ValueError("Unknown criticality")
    fault_map = {}
    for row in value["faults"]:
        fields(row, {"id", "title", "requirements"})
        title(row["title"])
        links(row["requirements"], reqs, 1)
        fault_map[row["id"]] = row
    test_map = {}
    for row in value["tests"]:
        fields(row, {"id", "title", "requirements", "faults", "definition"})
        title(row["title"])
        text(row["definition"], r"[a-f0-9]{64}")
        links(row["requirements"], reqs, 1)
        links(row["faults"], faults)
        if any(
            not set(fault_map[f]["requirements"]) & set(row["requirements"]) for f in row["faults"]
        ):
            raise ValueError("Fault and test have no common requirement")
        test_map[row["id"]] = row
    attempts = set()
    for row in value["results"]:
        fields(
            row,
            {
                "id",
                "test",
                "attempt",
                "completed",
                "source",
                "definition",
                "baselines",
                "status",
                "artifact",
            },
        )
        text(row["test"])
        if row["test"] not in tests:
            raise ValueError("Unknown test result")
        integer(row["attempt"], 1, 1000000)
        integer(row["completed"], 1, 4102444800)
        for key, length in (("source", 40), ("definition", 64), ("artifact", 64)):
            text(row[key], rf"[a-f0-9]{{{length}}}")
        fields(row["baselines"], set(test_map[row["test"]]["requirements"]))
        for revision in row["baselines"].values():
            integer(revision, 1, 10000)
        if row["status"] not in ("pass", "fail", "error", "skipped"):
            raise ValueError("Unknown test status")
        attempt_key = row["test"], row["attempt"]
        if attempt_key in attempts:
            raise ValueError("Ambiguous attempt")
        attempts.add(attempt_key)
    fields(value["release"], {"source", "artifact"})
    text(value["release"]["source"], r"[a-f0-9]{40}")
    text(value["release"]["artifact"], r"[a-f0-9]{64}")
    return copy.deepcopy(value)


def fixture(settings: Settings) -> dict[str, Any]:
    """Build deterministic fictional spacecraft recorder evidence, including deliberate regressions."""
    requirements = [
        {
            "id": "REQ-STORE",
            "title": "Recorder preserves accepted samples",
            "revision": 1,
            "criticality": "critical",
        },
        {
            "id": "REQ-RECOVER",
            "title": "Recorder recovers after simulated reset",
            "revision": 1,
            "criticality": "critical",
        },
        {
            "id": "REQ-REJECT",
            "title": "Malformed samples produce a diagnostic",
            "revision": 1,
            "criticality": "standard",
        },
    ]
    tests = [
        {
            "id": "TEST-STORE",
            "title": "Round-trip synthetic samples",
            "requirements": ["REQ-STORE"],
            "faults": [],
            "definition": "1" * 64,
        },
        {
            "id": "TEST-RESET",
            "title": "Simulated reset recovery",
            "requirements": ["REQ-RECOVER"],
            "faults": ["FAULT-RESET"],
            "definition": "2" * 64,
        },
        {
            "id": "TEST-INVALID",
            "title": "Reject truncated sample",
            "requirements": ["REQ-REJECT"],
            "faults": ["FAULT-INPUT"],
            "definition": "3" * 64,
        },
    ]
    results = [
        {
            "id": "RESULT-" + str(i),
            "test": t["id"],
            "attempt": 1,
            "completed": NOW - 1800,
            "source": SHA,
            "definition": t["definition"],
            "baselines": {r: 1 for r in t["requirements"]},
            "status": "pass",
            "artifact": str(i) * 64,
        }
        for i, t in enumerate(tests, 1)
    ]
    value: dict[str, Any] = {
        "schema": 1,
        "title": "Fictional spacecraft recorder",
        "source": SHA,
        "as_of": NOW,
        "max_age": settings.max_age,
        "requirements": requirements,
        "tests": tests,
        "faults": [
            {
                "id": "FAULT-RESET",
                "title": "Reset during collection",
                "requirements": ["REQ-RECOVER"],
            },
            {"id": "FAULT-INPUT", "title": "Truncated sample", "requirements": ["REQ-REJECT"]},
        ],
        "results": results,
        "release": {"source": SHA, "artifact": "e" * 64},
    }
    if settings.scenario == "missing":
        requirements.append(
            {
                "id": "REQ-NEW",
                "title": "New requirement without a test",
                "revision": 1,
                "criticality": "standard",
            }
        )
    elif settings.scenario == "stale":
        requirements[0]["revision"] = 2
    elif settings.scenario == "regression":
        newer = copy.deepcopy(results[0])
        newer.update(id="RESULT-NEW", attempt=2, completed=NOW - 900, status="fail")
        results.append(newer)
    elif settings.scenario == "fault-gap":
        tests[1]["faults"] = []
    elif settings.scenario == "mixed":
        results[0]["completed"] = NOW - 700000
        results[1]["source"] = "b" * 40
        results[2]["status"] = "skipped"
        value["release"]["source"] = "c" * 40
    return validate(value)


def load_input(path: Path) -> dict[str, Any]:
    """Read at most 1 MiB of regular UTF-8 duplicate-safe JSON and validate its complete graph."""
    return validate(load_json(path, 1024 * 1024))


def catalog() -> dict[str, Any]:
    """Expose finite demo labels and second-based age options for the local browser."""
    return {
        "scenarios": CASES,
        "choices": CHOICES,
        "defaults": {"scenario": "complete", "max_age": 86400},
    }
