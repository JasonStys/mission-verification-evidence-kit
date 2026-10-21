"""Bounded JUnit-to-traceability adapter by Jason Stys; never execute submitted commands.

Function import_junit maps a fixed reviewed demonstration suite, not arbitrary XML claims.
Variables EXPECTED, source, completed, digest. Exact lines: docs/CODE_INDEX.md.
"""

import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from evidencekit.delivery.io import read_bytes
from evidencekit.model import Settings, fixture, integer, text, validate

EXPECTED = {
    "test_recorder_roundtrip": "TEST-STORE",
    "test_recorder_reset": "TEST-RESET",
    "test_recorder_invalid": "TEST-INVALID",
}


def import_junit(path: Path, source: str, completed: int, definition: str) -> dict[str, Any]:
    """Map exactly three known test cases; reject entities/duplicates/unknowns and bind caller-supplied context."""
    text(source, r"[a-f0-9]{40}")
    text(definition, r"[a-f0-9]{64}")
    integer(completed, 1, 4102444800)
    data = read_bytes(path, 1024 * 1024)
    # UTF-8 only: a UTF-16 declaration cannot bypass the entity/DTD guard.
    try:
        decoded = data.decode("utf-8")
        if "<!DOCTYPE" in decoded.upper() or "<!ENTITY" in decoded.upper() or "\x00" in decoded:
            raise ValueError("DTD/entities are not accepted")
        root = ET.fromstring(decoded)
    except (UnicodeError, ET.ParseError) as error:
        raise ValueError("Invalid UTF-8 JUnit") from error
    if root.tag not in ("testsuite", "testsuites"):
        raise ValueError("Expected JUnit suites")
    for suite in root.iter():
        if suite.tag not in ("testsuite", "testsuites"):
            continue
        local_cases = list(suite.iter("testcase"))
        counts = {
            "tests": len(local_cases),
            "failures": sum(c.find("failure") is not None for c in local_cases),
            "errors": sum(c.find("error") is not None for c in local_cases),
            "skipped": sum(c.find("skipped") is not None for c in local_cases),
        }
        for key, expected in counts.items():
            declared = suite.get(key)
            if declared is not None and (
                not declared.isascii() or not declared.isdigit() or int(declared) != expected
            ):
                raise ValueError("Contradictory suite counts")
    cases = list(root.iter("testcase"))
    if any(
        child.tag not in {"failure", "error", "skipped", "properties", "system-out", "system-err"}
        for case in cases
        for child in case
    ):
        raise ValueError("Unsupported test case element")
    if len(cases) != 3 or {case.get("name") for case in cases} != set(EXPECTED):
        raise ValueError("Expected exactly the reviewed recorder test cases")
    if any(
        node.tag in ("failure", "error", "skipped")
        for node in root.iter()
        if node not in [child for case in cases for child in case.iter()]
    ):
        raise ValueError("Unmapped suite-level failure")
    value = fixture(Settings())
    value.update(source=source, as_of=completed)
    value["release"]["source"] = source
    digest = hashlib.sha256(data).hexdigest()
    for test in value["tests"]:
        test["definition"] = definition
    for result in value["results"]:
        case = next(case for case in cases if EXPECTED[case.get("name", "")] == result["test"])
        outcomes = [tag for tag in ("failure", "error", "skipped") if case.find(tag) is not None]
        if len(outcomes) > 1:
            raise ValueError("Conflicting JUnit outcomes")
        status = (
            {"failure": "fail", "error": "error", "skipped": "skipped"}.get(outcomes[0], "pass")
            if outcomes
            else "pass"
        )
        result.update(
            source=source,
            completed=completed,
            definition=definition,
            artifact=digest,
            status=status,
        )
    return validate(value)
