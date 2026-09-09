from __future__ import annotations

import pytest
from _regression_helpers import (
    OM_BOXTEST_NAMES,
    assert_matches_expected,
    assert_results_identical,
    run_scenario,
)


@pytest.mark.parametrize("name", OM_BOXTEST_NAMES)
def test_two_runs_in_same_process_match_and_are_consistent(name, tmp_path):
    run1_dir = tmp_path / "run1"
    run2_dir = tmp_path / "run2"
    run1_dir.mkdir()
    run2_dir.mkdir()

    result1 = run_scenario(name, run1_dir)
    result2 = run_scenario(name, run2_dir)

    assert_matches_expected(result1, name)
    assert_matches_expected(result2, name)
    assert_results_identical(result1, result2)
