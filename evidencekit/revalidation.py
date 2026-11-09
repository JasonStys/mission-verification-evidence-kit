"""Actionable declared-evidence revalidation queue by Jason Stys.

Function: revalidation_queue. Variables: immutable current baselines, affected requirements,
freshness deadlines and structural coverage gaps. Exact lines: docs/CODE_INDEX.md.
This plans human review; it never waives a gate, authenticates evidence or runs a test.
"""

from typing import Any


def revalidation_queue(
    value: dict[str, Any], tests: list[dict[str, Any]], requirements: list[dict[str, Any]]
) -> dict[str, Any]:
    """Prioritize blocked critical evidence then freshness, preserving exact expected metadata.

    Freshness accepts age==max_age, so the first invalid integer second is completed+max_age+1.
    Chronology conflicts need evidence investigation; a rerun alone does not erase that history.
    """
    definitions = {test["id"]: test for test in value["tests"]}
    baselines = {requirement["id"]: requirement for requirement in value["requirements"]}
    queue = []
    for test in tests:
        result = test["result"]
        expires = result["completed"] + value["max_age"] + 1 if test["accepted"] else None
        queue.append(
            {
                "test": test["id"],
                "state": "maintain-freshness" if test["accepted"] else "blocked",
                "critical": any(
                    baselines[req]["criticality"] == "critical" for req in test["requirements"]
                ),
                "requirements": test["requirements"],
                "reasons": test["reasons"],
                "first_invalid_second": expires,
                "seconds_until_invalid": expires - value["as_of"] if expires is not None else None,
                "action": "investigate-chronology-before-revalidation"
                if "chronology-conflict" in test["reasons"]
                else "capture-current-test-evidence"
                if not test["accepted"]
                else "schedule-revalidation-before-expiry",
                "expected": {
                    "source": value["source"],
                    "definition": definitions[test["id"]]["definition"],
                    "baselines": {req: baselines[req]["revision"] for req in test["requirements"]},
                },
            }
        )
    queue.sort(
        key=lambda item: (
            item["state"] != "blocked",
            not item["critical"],
            item["first_invalid_second"] if item["first_invalid_second"] is not None else 0,
            item["test"],
        )
    )
    gaps = []
    for requirement in requirements:
        if not requirement["tests"]:
            gaps.append(
                {"requirement": requirement["id"], "kind": "missing-procedure", "fault": None}
            )
        for fault in requirement["uncovered_faults"]:
            configured = [
                test["id"]
                for test in tests
                if requirement["id"] in test["requirements"] and fault in test["faults"]
            ]
            gaps.append(
                {
                    "requirement": requirement["id"],
                    "fault": fault,
                    "kind": "revalidate-linked-tests" if configured else "add-fault-test-link",
                    "configured_tests": configured,
                }
            )
    deadlines = [
        item["first_invalid_second"] for item in queue if item["first_invalid_second"] is not None
    ]
    return {
        "as_of": value["as_of"],
        "tests": queue,
        "coverage_gaps": gaps,
        "next_expiry_second": min(deadlines) if deadlines else None,
        "release_source_action": None
        if value["release"]["source"] == value["source"]
        else "reconcile-release-source-with-candidate-before-gating",
    }
