"""Convert actual reviewed-suite JUnit into gateable inputs by Jason Stys.

Function main; variables input/output/source/definition. Index: docs/CODE_INDEX.md.
Caller must independently provide tested source and test-definition SHA; no provenance is inferred.
"""

import argparse
from pathlib import Path

from evidencekit.delivery.io import canonical
from evidencekit.junit import import_junit


def main() -> None:
    """Write a new evidence input only after strict XML/context validation; refuse replacement."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", type=Path, required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--definition", required=True)
    parser.add_argument("--completed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = import_junit(args.junit, args.source, args.completed, args.definition)
    with args.output.open("xb") as stream:
        stream.write(canonical(value))
    print("Saved declared JUnit evidence, not authenticated provenance")


if __name__ == "__main__":
    main()
