from __future__ import annotations

import numpy as np
import pandas as pd

from .survey import by_age_group


def rate_by_age_group(survey: pd.DataFrame, measure: str | int) -> np.ndarray:
    values = by_age_group(survey, measure)
    n_host = by_age_group(survey, "nHost")
    with np.errstate(divide="ignore", invalid="ignore"):
        return values / n_host


def prevalence(survey: pd.DataFrame) -> np.ndarray:
    return rate_by_age_group(survey, "nPatent")


def total_rate(survey: pd.DataFrame, measure: str | int) -> np.ndarray:
    values = by_age_group(survey, measure).sum(axis=0)
    n_host = by_age_group(survey, "nHost").sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return values / n_host


def pfpr(
    survey: pd.DataFrame,
    upperbounds: np.ndarray,
    lo: float = 2.0,
    hi: float = 10.0,
    survey_index: int = -1,
    lowerbound: float = 0.0,
) -> float:
    upperbounds = np.asarray(upperbounds, dtype=float)
    lowerbounds = np.concatenate([[lowerbound], upperbounds[:-1]])
    in_range = (lowerbounds >= lo) & (upperbounds <= hi)
    n_host = by_age_group(survey, "nHost")[in_range, survey_index].sum()
    n_patent = by_age_group(survey, "nPatent")[in_range, survey_index].sum()
    return float(n_patent / n_host) if n_host > 0 else float("nan")
