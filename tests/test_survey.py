from __future__ import annotations

import numpy as np
import pandas as pd
from openmalaria import MEASURE_CODES

from openmalaria_tools import survey as oms


def test_age_groups(survey):
    assert list(oms.age_groups(survey)) == [1, 2, 3]
    assert oms.n_age_groups(survey) == 3


def test_by_age_group_is_age_group_by_survey(survey):
    n_host = oms.by_age_group(survey, "nHost")
    assert n_host.shape == (3, 2)
    assert np.array_equal(n_host, [[100.0, 200.0], [50.0, 0.0], [10.0, 20.0]])


def test_by_age_group_accepts_measure_code(survey):
    assert np.array_equal(
        oms.by_age_group(survey, MEASURE_CODES["nPatent"]),
        oms.by_age_group(survey, "nPatent"),
    )


def test_read_output_txt_matches_survey_schema(survey, tmp_path):
    path = tmp_path / "output.txt"
    survey.to_csv(path, sep="\t", header=False, index=False)

    read = oms.read_output_txt(path)

    assert list(read.columns) == oms.SURVEY_COLUMNS
    pd.testing.assert_frame_equal(read, survey, check_dtype=False)
