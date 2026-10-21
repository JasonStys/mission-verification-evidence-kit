"""Reviewed evidence contracts plus informational Python resource measurement by Jason Stys.

Function main. Variables: cases, requirement summaries, elapsed seconds, traced allocation peak.
Exact lines: docs/CODE_INDEX.md. Timing/allocation are not universal performance or total process RSS.
"""

import argparse
import json
import time
import tracemalloc
from pathlib import Path

from evidencekit.engine import build_run
from evidencekit.model import CASES, Settings


def main() -> None:
    """Check deterministic evidence summaries against reviewed contracts; update only with explicit --write."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    start = time.perf_counter()
    tracemalloc.start()
    cases = {name: build_run(Settings(scenario=name))["summary"] for name in CASES}
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    path = Path(__file__).resolve().parents[1] / "docs/reports/benchmark.json"
    if args.write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cases, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(path.read_bytes()) != cases:
        raise SystemExit("Case contract drift: review numerical changes before updating")
    print(
        f"6 evidence case contracts passed; {time.perf_counter() - start:.3f} s; Python traced peak {peak} bytes (not RSS)"
    )


if __name__ == "__main__":
    main()
