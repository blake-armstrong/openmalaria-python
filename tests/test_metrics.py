from __future__ import annotations

import math

import numpy as np
from conftest import make_survey

from openmalaria_tools import metrics


def test_prevalence(survey):
    expected = [[0.1, 0.2], [0.5, np.nan], [0.1, 0.25]]
    assert np.allclose(metrics.prevalence(survey), expected, equal_nan=True)


def test_rate_by_age_group(survey):
    expected = [[0.05, 0.04], [0.04, np.nan], [0.0, 0.05]]
    assert np.allclose(
        metrics.rate_by_age_group(survey, "nUncomp"), expected, equal_nan=True
    )


def test_total_rate(survey):
    assert np.allclose(metrics.total_rate(survey, "nUncomp"), [7 / 160, 9 / 220])


def test_pfpr_selects_age_groups_inside_range():
    upperbounds = np.array([0.5, 1, 2, 5, 10, 15, 99])
    n_host = [[float(10 * (i + 1))] for i in range(len(upperbounds))]
    n_patent = [[float(i + 1)] for i in range(len(upperbounds))]
    survey = make_survey({"nHost": n_host, "nPatent": n_patent})

    assert math.isclose(metrics.pfpr(survey, upperbounds), (4 + 5) / (40 + 50))


def test_pfpr_is_nan_without_hosts():
    survey = make_survey({"nHost": [[0.0], [0.0]], "nPatent": [[0.0], [0.0]]})
    assert math.isnan(metrics.pfpr(survey, np.array([5.0, 10.0])))
