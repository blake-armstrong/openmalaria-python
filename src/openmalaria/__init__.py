from __future__ import annotations

import os
import pickle
import subprocess
import sys
import tempfile
from typing import Optional

from ._openmalaria import _version
from .errors import OpenMalariaError
from .types import OMRunResult, ScenarioResult

__all__ = ["OMRunResult", "OpenMalariaError", "ScenarioResult", "run", "version"]


def run(
    *,
    xml: Optional[str] = None,
    path: Optional[str] = None,
    resource_path: str = "",
    validate_only: bool = False,
    verbose: bool = False,
    progress: bool = False,
    seed: Optional[int] = None,
) -> OMRunResult:
    if (xml is None) == (path is None):
        raise ValueError("exactly one of xml= or path= must be given")

    job = {
        "xml": xml,
        "path": path,
        "resource_path": resource_path,
        "validate_only": validate_only,
        "verbose": verbose,
        "progress": progress,
        "seed": seed,
    }

    with tempfile.TemporaryDirectory(prefix="openmalaria-run-") as tmp:
        in_path = os.path.join(tmp, "in.pkl")
        out_path = os.path.join(tmp, "out.pkl")
        with open(in_path, "wb") as f:
            pickle.dump(job, f)

        package_dir = os.path.dirname(os.path.abspath(__file__))
        worker_launch_dir = os.path.dirname(package_dir)
        proc = subprocess.run(
            [
                sys.executable, "-m", "openmalaria._worker",
                "--in", in_path, "--out", out_path, "--cwd", os.getcwd(),
            ],
            cwd=worker_launch_dir,
        )

        if not os.path.exists(out_path):
            raise OpenMalariaError(
                f"openmalaria worker subprocess exited with code {proc.returncode} "
                "before producing a result (likely crashed -- see output above)"
            )

        with open(out_path, "rb") as f:
            outcome = pickle.load(f)

    if not outcome["ok"]:
        raise OpenMalariaError(outcome["error"])
    return outcome["result"]


def version() -> dict:
    v = _version()
    return {"program_version": v.program_version, "schema_version": v.schema_version}
