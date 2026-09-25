from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from openmalaria import MEASURE_CODES

SURVEY_COLUMNS = ["survey", "column", "measure", "value"]


def measure_code(measure: str | int) -> int:
    return MEASURE_CODES[measure] if isinstance(measure, str) else measure


def age_groups(survey: pd.DataFrame) -> np.ndarray:
    return np.unique(survey.loc[survey["survey"] == 1, "column"].to_numpy())


def n_age_groups(survey: pd.DataFrame) -> int:
    return len(age_groups(survey))


def by_age_group(survey: pd.DataFrame, measure: str | int) -> np.ndarray:
    rows = survey[survey["measure"] == measure_code(measure)]
    return np.array(
        [
            rows.loc[rows["column"] == age_group, "value"].to_numpy()
            for age_group in range(1, n_age_groups(survey) + 1)
        ]
    )


def read_output_txt(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", header=None, names=SURVEY_COLUMNS)
