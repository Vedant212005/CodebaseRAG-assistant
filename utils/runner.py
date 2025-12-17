import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable  # ensures correct python env

def run_ingest(repo_path: str):
    repo_path = str(Path(repo_path).resolve())

    result = subprocess.run(
        [PYTHON, "ingest.py", repo_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(
            f"ingest.py failed:\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )


def run_build_vector():
    result = subprocess.run(
        [PYTHON, "build_vector_index.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(
            f"build_vector.py failed:\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )


