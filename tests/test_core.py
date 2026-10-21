"""Traceability, mutation, boundary, property and private-history tests by Jason Stys.

Functions and fixture variable lines: docs/CODE_INDEX.md. Never execute declared evidence.
"""

import copy
import hashlib
import json
import sqlite3
from contextlib import closing

import pytest
from hypothesis import given
from hypothesis import strategies as st

from evidencekit.__main__ import main
from evidencekit.delivery.io import canonical
from evidencekit.engine import analyze, build_run
from evidencekit.model import CASES, NOW, Settings, fixture, load_input, validate
from evidencekit.reports import export_report, save_history


@pytest.mark.parametrize(
    "case,blocked",
    [
        ("complete", 0),
        ("missing", 1),
        ("stale", 1),
        ("regression", 1),
        ("fault-gap", 1),
        ("mixed", 3),
    ],
)
def test_reviewed_cases(case, blocked):
    """Reviewed fault fixtures agree with independent SQL and cannot imply authenticated provenance."""
    run = build_run(Settings(case))
    assert run["summary"]["blocked"] == blocked
    assert run["verification"]["sql_agrees"]
    assert not run["verification"]["provenance_authenticated"]
    body = dict(run)
    identity = body.pop("id")
    assert identity == hashlib.sha256(canonical(body)).hexdigest()


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("status", "fail", "fail"),
        ("status", "skipped", "skipped"),
        ("status", "error", "error"),
        ("source", "b" * 40, "source-mismatch"),
        ("definition", "b" * 64, "definition-mismatch"),
        ("completed", NOW + 1, "future-result"),
        ("completed", NOW - 86401, "expired"),
    ],
)
def test_unacceptable_results(field, value, reason):
    """Each stale, future, failed, skipped or errored record blocks its requirement."""
    value_in = fixture(Settings())
    value_in["results"][0][field] = value
    run = analyze(value_in)
    assert run["summary"]["blocked"] == 1
    assert reason in next(t for t in run["tests"] if t["id"] == "TEST-STORE")["reasons"]


def test_missing_chronology_and_all_tests():
    """Missing evidence and clock conflicts block; adding a second failing linked test also blocks."""
    value = fixture(Settings())
    value["results"].pop(0)
    assert analyze(value)["summary"]["blocked"] == 1
    value = fixture(Settings())
    newer = copy.deepcopy(value["results"][0])
    newer.update(id="NEW", attempt=2, completed=NOW - 2000)
    value["results"].append(newer)
    assert "chronology-conflict" in analyze(value)["tests"][-1]["reasons"]
    value = fixture(Settings())
    extra = copy.deepcopy(value["tests"][0])
    extra["id"] = "EXTRA"
    value["tests"].append(extra)
    assert not analyze(value)["summary"]["ready"]


@given(
    st.integers(min_value=0, max_value=100000),
    st.sampled_from(["pass", "fail", "skipped", "error"]),
)
def test_sql_python_differential(age, status):
    """Randomized freshness and outcome mutations must always yield the same relational verdict."""
    value = fixture(Settings())
    value["results"][0].update(completed=NOW - age, status=status)
    run = analyze(value)
    assert run["summary"]["ready"] == (age <= 86400 and status == "pass")


@given(st.permutations([0, 1, 2]))
def test_record_order_does_not_change_verdict(order):
    """Input collection order never selects a different attempt or requirement verdict."""
    value = fixture(Settings())
    expected = analyze(value)
    value["results"] = [value["results"][i] for i in order]
    value["tests"].reverse()
    value["requirements"].reverse()
    actual = analyze(value)
    assert actual["requirements"] == expected["requirements"]
    assert actual["tests"] == expected["tests"]


@pytest.mark.parametrize(
    "path,bad",
    [
        (("schema",), True),
        (("schema",), 2),
        (("as_of",), 0),
        (("max_age",), 0),
        (("title",), ""),
        (("title",), "bad\nline"),
        (("title",), "x" * 161),
        (("source",), "x"),
        (("requirements",), []),
        (("tests",), {}),
        (("faults",), [{}]),
        (("results",), [None]),
        (("requirements", 0, "criticality"), "optional"),
        (("requirements", 0, "revision"), False),
        (("tests", 0, "requirements"), ["MISSING"]),
        (("tests", 0, "requirements"), ["REQ-STORE"] * 2),
        (("tests", 0, "faults"), ["FAULT-RESET"]),
        (("tests", 0, "definition"), 1),
        (("results", 0, "test"), "UNKNOWN"),
        (("results", 0, "attempt"), 0),
        (("results", 0, "status"), "success"),
        (("results", 0, "baselines"), {}),
        (("release", "artifact"), "g" * 64),
    ],
)
def test_input_rejections(path, bad):
    """Invalid types, references, controls, duplicate links and unknown outcomes cannot be coerced."""
    value = fixture(Settings())
    target = value
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = bad
    with pytest.raises(ValueError):
        validate(value)


def test_duplicate_and_unknown_fields():
    """Duplicate attempt/ID and undeclared fields are rejected rather than deduplicated silently."""
    for collection in ("requirements", "tests", "faults", "results"):
        value = fixture(Settings())
        value[collection].append(copy.deepcopy(value[collection][0]))
        with pytest.raises(ValueError):
            validate(value)
    value = fixture(Settings())
    extra = copy.deepcopy(value["results"][0])
    extra["id"] = "NEW"
    value["results"].append(extra)
    with pytest.raises(ValueError):
        validate(value)
    value = fixture(Settings())
    value["extra"] = 1
    with pytest.raises(ValueError):
        validate(value)


@pytest.mark.parametrize(
    "raw", [b'{"schema":1,"schema":1}', b'{"schema":NaN}', b"\xff", b"{", b"[" * 1200 + b"]" * 1200]
)
def test_bounded_decode(tmp_path, raw):
    """Malformed UTF-8, duplicate JSON keys, constants and deep documents fail without partial reports."""
    path = tmp_path / "input.json"
    path.write_bytes(raw)
    with pytest.raises(ValueError):
        load_input(path)


def test_oversize_and_no_alias(tmp_path):
    """Bound JSON size and return an independent validated copy."""
    path = tmp_path / "input.json"
    path.write_bytes(b" " * (1024 * 1024 + 1))
    with pytest.raises(ValueError):
        load_input(path)
    value = fixture(Settings())
    clone = validate(value)
    clone["title"] = "Changed"
    assert value["title"] != clone["title"]


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("format_name", ["json", "input", "csv", "html"])
def test_exports(case, format_name):
    """All fixtures export full inert reports and replay inputs without lossy conversions."""
    run = build_run(Settings(case))
    body, content_type = export_report(run, format_name)
    assert body and content_type
    if format_name == "json":
        assert json.loads(body) == run
    if format_name == "input":
        assert analyze(json.loads(body)) == run
    if format_name == "csv":
        assert b"id,title,revision" in body
    if format_name == "html":
        assert b"<script" not in body


def test_inert_exports_and_history(tmp_path):
    """Escape HTML, neutralize CSV formulas, bind SQLite and enforce immutable/idempotent identities."""
    value = fixture(Settings())
    value["requirements"][0]["title"] = "=2+2<script>"
    run = analyze(value)
    assert b"'=2+2" in export_report(run, "csv")[0]
    assert b"&lt;script&gt;" in export_report(run, "html")[0]
    with pytest.raises(ValueError):
        export_report(run, "exe")
    path = tmp_path / "history.sqlite3"
    save_history(path, run)
    save_history(path, run)
    with closing(sqlite3.connect(path)) as db:
        assert db.execute("SELECT count(*) FROM runs").fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("UPDATE runs SET report_json='{}'")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("DELETE FROM runs")
    broken = copy.deepcopy(run)
    broken["summary"]["ready"] = False
    with pytest.raises(ValueError):
        save_history(path, broken)
    for i in range(99):
        value["title"] = "Variant " + str(i)
        save_history(path, analyze(value))
    value["title"] = "Full"
    with pytest.raises(ValueError):
        save_history(path, analyze(value))


def test_cli_gate_and_exports(tmp_path, capsys):
    """Actual CLI reports distinct success/blocked/invalid exits and refuses overwrites."""
    path = tmp_path / "input.json"
    path.write_bytes(canonical(fixture(Settings())))
    assert main(["gate", "--input", str(path)]) == 0
    path.write_bytes(canonical(fixture(Settings("regression"))))
    assert main(["gate", "--input", str(path)]) == 2
    out = tmp_path / "report.json"
    assert main(["export", "--input", str(path), "--output", str(out)]) == 0
    assert main(["export", "--output", str(out)]) == 1
    assert main(["gate", "--input", str(tmp_path / "missing")]) == 1
    capsys.readouterr()


def test_independent_sql_disagreement(monkeypatch):
    """A checker disagreement suppresses the entire report, not just its verification badge."""
    monkeypatch.setattr("evidencekit.engine.sql_reference", lambda value: [])
    with pytest.raises(RuntimeError):
        build_run(Settings())


@pytest.mark.parametrize("settings", [{"scenario": "unknown"}, {"max_age": True}, {"max_age": 2}])
def test_settings(settings):
    """Browser/CLI scenarios and freshness options are finite, not arbitrary expression input."""
    with pytest.raises(ValueError):
        Settings(**settings)
