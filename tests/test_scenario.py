from __future__ import annotations

import numpy as np
import pytest

from openmalaria_tools import scenario

XML = """<om:scenario xmlns:om="http://openmalaria.org/schema/scenario_50">
  <demography>
    <ageGroup lowerbound="0.0">
      <group poppercent="50" upperbound="20" />
      <group poppercent="50" upperbound="90" />
    </ageGroup>
  </demography>
  <monitoring>
    <ageGroup lowerbound="0.0">
      <group upperbound="0.5" />
      <group upperbound="2" />
      <group upperbound="10" />
      <group upperbound="99" />
    </ageGroup>
  </monitoring>
</om:scenario>
"""


def test_age_group_bounds_uses_monitoring_not_demography():
    assert np.array_equal(scenario.age_group_bounds(XML), [0.0, 0.5, 2.0, 10.0, 99.0])
    assert np.array_equal(scenario.age_group_upperbounds(XML), [0.5, 2.0, 10.0, 99.0])


def test_age_group_midpoints():
    assert np.allclose(scenario.age_group_midpoints(XML), [0.25, 1.25, 6.0, 54.5])


def test_age_group_labels():
    upperbounds = scenario.age_group_upperbounds(XML)
    assert scenario.age_group_labels(upperbounds) == ["0-0.5", "0.5-2", "2-10", "10-99"]


def test_missing_monitoring_age_group_raises():
    with pytest.raises(ValueError):
        scenario.age_group_bounds("<scenario><monitoring/></scenario>")
