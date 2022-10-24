"""
Shell Helpers
-------------

Helpers for working with shell commands.
"""

from typing import Tuple
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


def run_command_in_dir(command: str, run_dir: Path = Path(".")) -> Tuple[int, str]:
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        # Use temp files not a PIPE, a PIPE has a tiny buffer than
        # can deadlock or result in eroneous resource exhaustion behaviour
        # where encountering some of our larger outputs (jsonSchemaErrors result
        # in large writes to stdout)
        Path(tmp_dir / "buffer").mkdir()
        stdout_path = Path(tmp_dir / "buffer" / "stdout")
        stderr_path = Path(tmp_dir / "buffer" / "stderr")

        with open(stdout_path, "w") as stdout_file, open(
            stderr_path, "w"
        ) as stderr_file:

            process = subprocess.Popen(
                command,
                shell=True,
                cwd=run_dir.resolve(),
                stdout=stdout_file,
                stderr=stderr_file,
            )

        status_code = process.wait()

        with open(stdout_path) as stdout_file, open(stderr_path) as stderr_file:
            response = stdout_file.read() + stderr_file.read()

        return status_code, response
