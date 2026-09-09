from __future__ import annotations

import pytest
from _regression_helpers import OM_BOXTEST_NAMES, assert_matches_expected, run_scenario


@pytest.mark.parametrize("name", OM_BOXTEST_NAMES)
def test_scenario_matches_expected(name, tmp_path):
    result = run_scenario(name, tmp_path)
    assert_matches_expected(result, name)
