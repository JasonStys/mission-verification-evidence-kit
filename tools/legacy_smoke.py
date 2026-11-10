"""Exercise a freshly reviewed frozen app by Jason Stys. Functions/variables: docs/CODE_INDEX.md."""

import json

if __package__:
    from .release_contract import require
else:
    from release_contract import require
import queue
import sqlite3
import subprocess
import sys
import tempfile
import threading
import urllib.request
from contextlib import closing
from pathlib import Path


def main(executable: Path) -> None:
    """Verify real exports, replay, SQL, notices and loopback web UI; always stop only this process."""
    executable = executable.resolve(strict=True)
    internal = executable.parent / "_internal"
    for name in (
        "project/LICENSE",
        "python/PYTHON.txt",
        "pyinstaller/COPYING.txt",
        "vite/LICENSE.md",
    ):
        require((internal / "licenses" / name).is_file(), name)
    with tempfile.TemporaryDirectory(prefix="mission-smoke-") as temporary:
        folder = Path(temporary)
        for format_name in ("json", "csv", "html", "input"):
            subprocess.run(
                [
                    str(executable),
                    "export",
                    "--scenario",
                    "regression",
                    "--format",
                    format_name,
                    "--output",
                    str(folder / format_name),
                    "--history",
                    str(folder / "history.sqlite3"),
                ],
                check=True,
                timeout=30,
            )
        result = json.loads((folder / "json").read_bytes())
        require(not result["summary"]["ready"], "Legacy native acceptance condition failed")
        require(result["verification"]["sql_agrees"], "Legacy native acceptance condition failed")
        require(result["summary"]["blocked"] == 1, "Legacy native acceptance condition failed")
        require(
            len((folder / "csv").read_text().splitlines()) == 4,
            "Legacy native acceptance condition failed",
        )
        require(
            b"<script" not in (folder / "html").read_bytes(),
            "Legacy native acceptance condition failed",
        )
        with closing(sqlite3.connect(folder / "history.sqlite3")) as db:
            require(
                db.execute("SELECT count(*) FROM runs").fetchone()[0] == 1,
                "Legacy native acceptance condition failed",
            )
        subprocess.run(
            [
                str(executable),
                "export",
                "--input",
                str(folder / "input"),
                "--output",
                str(folder / "replayed.json"),
            ],
            check=True,
            timeout=30,
        )
        require(
            json.loads((folder / "replayed.json").read_bytes()) == result,
            "Legacy native acceptance condition failed",
        )
    process = subprocess.Popen(
        [str(executable), "serve", "--no-browser"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    lines: queue.Queue[str] = queue.Queue()

    def read_output() -> None:
        """Read owned process stdout off-thread so startup cannot wait without a deadline."""
        require(process.stdout, "Legacy native acceptance condition failed")
        for line in process.stdout:
            lines.put(line.strip())

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    try:
        url = ""
        for _ in range(6):
            line = lines.get(timeout=15)
            if line.startswith("http://127.0.0.1:"):
                url = line
                break
        require(url, "Legacy native acceptance condition failed")
        for route in ("api/health", "", "api/run"):
            with urllib.request.urlopen(url + route, timeout=30) as response:
                body = response.read()
                if not route:
                    require(
                        b"MISSION / VERIFY" in body and b"/assets/" in body,
                        "Legacy native acceptance condition failed",
                    )
                elif route == "api/run":
                    run = json.loads(body)
                    require(
                        len(run["requirements"]) == 3, "Legacy native acceptance condition failed"
                    )
                    require(
                        run["verification"]["sql_agrees"],
                        "Legacy native acceptance condition failed",
                    )
                else:
                    require(
                        json.loads(body)["status"] == "ok",
                        "Legacy native acceptance condition failed",
                    )
        print("Frozen evidence engine, all exports, replay, SQL, notices and HTTP UI passed")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        reader.join(timeout=3)
        if process.stdout:
            process.stdout.close()


if __name__ == "__main__":
    main(Path(sys.argv[1]))
