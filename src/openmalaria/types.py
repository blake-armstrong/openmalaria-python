from __future__ import annotations

from typing import TypedDict

import pandas as pd


class OMRunResult(TypedDict):
    """The dict openmalaria.run() itself returns."""

    survey: pd.DataFrame
    continuous: pd.DataFrame | None


class ScenarioResult(OMRunResult):
    """An OMRunResult tagged with the scenario it came from.

    Convenience for callers batching multiple run()s (e.g. one per work item
    in a parameter sweep) who want the name carried alongside the result
    rather than tracked separately.
    """

    name: str
