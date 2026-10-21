"""Local evidence-kit CLI by Jason Stys. Function main and argument locations: docs/CODE_INDEX.md.

No hardware/shell commands; optional delivery verification contacts GitHub through trusted gh.
Output files are create-only. The browser and mission graph have no external data sources.
"""

import argparse
import sqlite3
import sys
import webbrowser
from pathlib import Path

from evidencekit.delivery.io import canonical
from evidencekit.delivery.verify import TrustPolicy, verify_release
from evidencekit.engine import ROOT, analyze, build_run
from evidencekit.model import CASES, CHOICES, Settings, load_input
from evidencekit.reports import export_report, save_history
from evidencekit.server import make_server


def main(argv: list[str] | None = None) -> int:
    """Launch read-only loopback UI or save explicitly requested, independently checked evidence."""
    parser = argparse.ArgumentParser(description="Mission Verification Evidence Kit by Jason Stys")
    commands = parser.add_subparsers(dest="command", required=True)
    serve = commands.add_parser("serve")
    serve.add_argument("--port", type=int, default=0)
    serve.add_argument("--no-browser", action="store_true")
    export = commands.add_parser("export")
    export.add_argument("--scenario", choices=CASES, default=Settings().scenario)
    for key, choices in CHOICES.items():
        export.add_argument("--" + key, type=int, choices=choices, default=getattr(Settings(), key))
    export.add_argument("--input", type=Path)
    export.add_argument("--output", type=Path, required=True)
    export.add_argument("--history", type=Path)
    export.add_argument("--format", choices=("json", "input", "csv", "html"), default="json")
    gate = commands.add_parser("gate", help="Read-only input gate; exits 2 for blocked evidence")
    gate.add_argument("--input", type=Path, required=True)
    delivery = commands.add_parser(
        "verify-delivery",
        help="Authenticate the existing secure-delivery demo, never execute its payload",
    )
    delivery.add_argument("--directory", type=Path, required=True)
    delivery.add_argument("--commit", required=True)
    delivery.add_argument("--version", required=True)
    delivery.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "gate":
            run = analyze(load_input(args.input))
            print(canonical(run).decode(), end="")
            return 0 if run["summary"]["ready"] else 2
        if args.command == "verify-delivery":
            if args.output.exists():
                raise FileExistsError("Destination already exists")
            policy = TrustPolicy(
                "JasonStys/secure-delivery-pipeline-lab", args.commit, args.version
            )
            manifest = verify_release(args.directory, policy)
            with args.output.open("xb") as stream:
                stream.write(
                    canonical(
                        {
                            "authenticated": True,
                            "policy": vars(policy),
                            "manifest": manifest,
                            "scope": "Existing secure-delivery release only; not mission evidence authentication",
                        }
                    )
                )
            print("Authenticated existing delivery assets; no payload executed")
            return 0
        if args.command == "export":
            if args.output.exists():
                raise FileExistsError("Destination already exists")
            settings = Settings(**{key: getattr(args, key) for key in ("scenario", *CHOICES)})
            run = analyze(load_input(args.input)) if args.input else build_run(settings)
            body, _ = export_report(run, args.format)
            if args.history:
                save_history(args.history, run)
            with args.output.open("xb") as stream:
                stream.write(body)
            print("Saved " + run["id"])
            return 0
        assets = ROOT / "web/dist"
        if not (assets / "index.html").is_file():
            raise OSError("Build web assets first")
        with make_server(assets, args.port) as server:
            url = f"http://127.0.0.1:{server.server_port}/"
            print("Mission Verification Evidence Kit by Jason Stys\n" + url, flush=True)
            if not args.no_browser:
                webbrowser.open(url)
            try:
                server.serve_forever(poll_interval=0.25)
            except KeyboardInterrupt:
                print("Evidence kit stopped.", flush=True)
        return 0
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as error:
        print(f"Cannot complete: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
