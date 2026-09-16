from __future__ import annotations

import os
import pickle
import subprocess
import sys
import tempfile
from typing import Optional

from . import _openmalaria
from .errors import OpenMalariaError
from .types import OMRunResult, ScenarioResult

__all__ = [
    "MEASURE_CODES",
    "OMRunResult",
    "OpenMalariaError",
    "ScenarioResult",
    "run",
    "version",
]

MEASURE_CODES: dict[str, int] = _openmalaria.MEASURE_CODES


def run(
    *,
    xml: Optional[str] = None,
    path: Optional[str] = None,
    resource_path: str = "",
    validate_only: bool = False,
    verbose: bool = False,
    progress: bool = False,
    seed: Optional[int] = None,
    tmp_dir: Optional[str] = None,
    keep_tmp: bool = False,
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

    if keep_tmp:
        tmp = tempfile.mkdtemp(prefix="openmalaria-run-", dir=tmp_dir)
    else:
        tmp = tempfile.TemporaryDirectory(prefix="openmalaria-run-", dir=tmp_dir)

    try:
        tmp_path = tmp if keep_tmp else tmp.name
        in_path = os.path.join(tmp_path, "in.pkl")
        out_path = os.path.join(tmp_path, "out.pkl")
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
            msg = (
                f"openmalaria worker subprocess exited with code {proc.returncode} "
                "before producing a result"
            )
            if keep_tmp:
                msg += f"; input/output pickles kept at {tmp_path}"
            raise OpenMalariaError(msg)

        with open(out_path, "rb") as f:
            outcome = pickle.load(f)
    finally:
        if not keep_tmp:
            tmp.cleanup()

    if keep_tmp:
        print(f"openmalaria: kept tmp files at {tmp_path}", file=sys.stderr)

    if not outcome["ok"]:
        raise OpenMalariaError(outcome["error"])
    return outcome["result"]


def version() -> dict:
    v = _openmalaria._version()
    return {"program_version": v.program_version, "schema_version": v.schema_version}
