"""Independent declared-evidence queue expectations by Jason Stys.

Functions: test_*; variables: freshness equality, blocked critical evidence and structural gaps.
Queue entries never change the independent SQL-backed gate. Lines: docs/CODE_INDEX.md.
"""

from copy import deepcopy

from evidencekit.engine import analyze, build_run
from evidencekit.model import Settings, fixture


def test_exact_freshness_boundary_and_expected_baselines():
    """Age equal to the policy is accepted; its next integer second is the first invalid instant."""
    value = fixture(Settings())
    value["results"][0]["completed"] = value["as_of"] - value["max_age"]
    run = analyze(value)
    queue = run["revalidation"]
    item = next(item for item in queue["tests"] if item["test"] == "TEST-STORE")
    assert item["state"] == "maintain-freshness" and item["seconds_until_invalid"] == 1
    assert queue["next_expiry_second"] == value["as_of"] + 1
    assert item["expected"]["baselines"] == {"REQ-STORE": 1}
    assert run["summary"]["ready"]
    later = deepcopy(value)
    later["as_of"] += 1
    late = analyze(later)
    assert late["revalidation"]["tests"][0]["state"] == "blocked"
    assert "expired" in late["revalidation"]["tests"][0]["reasons"]


def test_regression_priority_structural_gap_and_release_action():
    """Newer failed critical tests rank first; missing links cannot be repaired by reruns alone."""
    regression = build_run(Settings(scenario="regression"))
    first = regression["revalidation"]["tests"][0]
    assert first["critical"] and first["state"] == "blocked" and "fail" in first["reasons"]
    missing = build_run(Settings(scenario="missing"))
    assert any(
        gap["kind"] == "missing-procedure" for gap in missing["revalidation"]["coverage_gaps"]
    )
    fault = build_run(Settings(scenario="fault-gap"))
    assert any(
        gap["kind"] == "add-fault-test-link" for gap in fault["revalidation"]["coverage_gaps"]
    )
    assert regression["summary"]["ready"] is False
    value = fixture(Settings())
    value["release"]["source"] = "f" * 40
    assert analyze(value)["revalidation"]["release_source_action"] is not None


def test_chronology_requires_investigation_and_unaccepted_fault_links_remain_visible():
    """Historical chronology conflict remains explicit rather than promising a rerun fixes it."""
    value = fixture(Settings())
    second = deepcopy(value["results"][1])
    second.update(id="RESULT-NEW", attempt=2, completed=second["completed"] - 1)
    value["results"].append(second)
    run = analyze(value)
    item = next(item for item in run["revalidation"]["tests"] if item["test"] == second["test"])
    assert item["action"] == "investigate-chronology-before-revalidation"
    assert any(
        gap["kind"] == "revalidate-linked-tests" for gap in run["revalidation"]["coverage_gaps"]
    )
    assert run["verification"]["sql_agrees"] and not run["summary"]["ready"]
