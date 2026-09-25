from __future__ import annotations

from openmalaria.types import OMRunResult

__all__ = ["OMRunResult", "ScenarioResult"]


class ScenarioResult(OMRunResult):
    """An OMRunResult tagged with the scenario it came from.

    Convenience for callers batching multiple run()s (e.g. one per work item
    in a parameter sweep) who want the name carried alongside the result
    rather than tracked separately.
    """

    name: str
