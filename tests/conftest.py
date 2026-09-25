from __future__ import annotations

import pandas as pd
import pytest
from openmalaria import MEASURE_CODES

N_AGE_GROUPS = 3
N_SURVEYS = 2


def make_survey(values: dict[str, list[list[float]]]) -> pd.DataFrame:
    rows = [
        (survey + 1, age_group + 1, MEASURE_CODES[name], by_group[age_group][survey])
        for name, by_group in values.items()
        for survey in range(len(by_group[0]))
        for age_group in range(len(by_group))
    ]
    return pd.DataFrame(rows, columns=["survey", "column", "measure", "value"])


@pytest.fixture
def survey() -> pd.DataFrame:
    return make_survey(
        {
            "nHost": [[100.0, 200.0], [50.0, 0.0], [10.0, 20.0]],
            "nPatent": [[10.0, 40.0], [25.0, 0.0], [1.0, 5.0]],
            "nUncomp": [[5.0, 8.0], [2.0, 0.0], [0.0, 1.0]],
        }
    )
