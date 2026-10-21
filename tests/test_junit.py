"""JUnit adapter adversarial and outcome tests by Jason Stys. Exact locations: docs/CODE_INDEX.md."""

import pytest

from evidencekit.engine import analyze
from evidencekit.junit import EXPECTED, import_junit
from evidencekit.model import NOW, SHA


@pytest.mark.parametrize(
    "outcome,ready", [("", True), ("failure", False), ("error", False), ("skipped", False)]
)
def test_actual_outcomes(tmp_path, outcome, ready):
    """Every test outcome maps explicitly, and non-passing outcomes prevent readiness."""
    path = tmp_path / "junit.xml"
    cases = "".join(
        f'<testcase name="{name}">{"<" + outcome + "/>" if index == 0 and outcome else ""}</testcase>'
        for index, name in enumerate(EXPECTED)
    )
    path.write_text(
        "<testsuites><testsuite>" + cases + "</testsuite></testsuites>", encoding="utf-8"
    )
    value = import_junit(path, SHA, NOW, "1" * 64)
    assert analyze(value)["summary"]["ready"] == ready
    assert len({r["artifact"] for r in value["results"]}) == 1


@pytest.mark.parametrize(
    "raw",
    [
        b"<bad/>",
        b"<",
        b"\xff",
        b'<!DOCTYPE x [<!ENTITY a "foo">]><testsuite/>',
        b"<testsuite/>",
        b'<testsuite><testcase name="unknown"/></testsuite>',
        b"\x00",
    ],
)
def test_xml_rejections(tmp_path, raw):
    """Unknown cases, entities, wrong encoding and incomplete suites cannot fabricate success."""
    path = tmp_path / "junit.xml"
    path.write_bytes(raw)
    with pytest.raises(ValueError):
        import_junit(path, SHA, NOW, "1" * 64)


def test_conflicts_and_suite_error(tmp_path):
    """Reject duplicate status elements and failures without any reviewed case mapping."""
    path = tmp_path / "junit.xml"
    cases = "".join(f'<testcase name="{name}"><failure/><skipped/></testcase>' for name in EXPECTED)
    path.write_text("<testsuite>" + cases + "</testsuite>", encoding="utf-8")
    with pytest.raises(ValueError):
        import_junit(path, SHA, NOW, "1" * 64)


@pytest.mark.parametrize("count", ["2", "4", "-3", "three", "٣"])
def test_contradictory_counts(tmp_path, count):
    """Aggregate counts cannot contradict the individually mapped cases or use ambiguous numeric text."""
    path = tmp_path / "junit.xml"
    cases = "".join(f'<testcase name="{name}"/>' for name in EXPECTED)
    path.write_text(f'<testsuite tests="{count}">{cases}</testsuite>', encoding="utf-8")
    with pytest.raises(ValueError):
        import_junit(path, SHA, NOW, "1" * 64)
    cases = "".join(f'<testcase name="{name}"/>' for name in EXPECTED)
    path.write_text("<testsuite><error/>" + cases + "</testsuite>", encoding="utf-8")
    with pytest.raises(ValueError):
        import_junit(path, SHA, NOW, "1" * 64)
