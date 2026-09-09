from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import openmalaria as om


def _read_expected_output(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path, sep="\t", header=None, names=["survey", "column", "measure", "value"]
    )


def _read_expected_ctsout(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", skiprows=1)


def test_survey_schema_and_values(scenario1_result, expected_output1):
    survey = scenario1_result["survey"]

    assert list(survey.columns) == ["survey", "column", "measure", "value"]
    assert survey["survey"].dtype.kind == "i"
    assert survey["column"].dtype.kind == "i"
    assert survey["measure"].dtype.kind == "i"
    assert survey["value"].dtype.kind == "f"
    assert len(survey) > 0

    expected = _read_expected_output(expected_output1)
    assert survey.shape == expected.shape
    assert (
        survey[["survey", "column", "measure"]].to_numpy()
        == expected[["survey", "column", "measure"]].to_numpy()
    ).all()
    assert np.allclose(
        survey["value"].to_numpy(), expected["value"].to_numpy(), rtol=1e-5, atol=1e-5
    )


def test_continuous_schema_and_values(scenario1_result, expected_ctsout1):
    continuous = scenario1_result["continuous"]
    assert continuous is not None

    expected = _read_expected_ctsout(expected_ctsout1)
    assert list(continuous.columns) == list(expected.columns)
    assert continuous.shape == expected.shape
    assert np.allclose(
        continuous.to_numpy(dtype=float),
        expected.to_numpy(dtype=float),
        rtol=1e-6,
        atol=1e-6,
        equal_nan=True,
    )


def test_version():
    v = om.version()
    assert set(v.keys()) == {"program_version", "schema_version"}
    assert isinstance(v["program_version"], str) and v["program_version"]
    assert isinstance(v["schema_version"], int) and v["schema_version"] > 0


def test_missing_scenario_raises(tmp_path):
    with pytest.raises(om.OpenMalariaError):
        om.run(path=str(tmp_path / "does_not_exist.xml"))


def test_xml_and_path_both_given_raises():
    with pytest.raises(ValueError):
        om.run(xml="<x/>", path="dummy.xml")


def test_neither_xml_nor_path_raises():
    with pytest.raises(ValueError):
        om.run()


def test_validate_only_is_fast_and_empty(scenario1_path, resource_path, monkeypatch):
    monkeypatch.chdir(scenario1_path.parent)
    r = om.run(
        path=str(scenario1_path), resource_path=resource_path, validate_only=True
    )
    assert r["survey"].shape == (0, 4)
    assert r["continuous"] is None


def test_xml_matches_path(scenario1_path, resource_path, monkeypatch):
    monkeypatch.chdir(scenario1_path.parent)
    xml_content = scenario1_path.read_text()
    r = om.run(xml=xml_content, resource_path=resource_path)
    assert r["survey"].shape[0] > 0
    assert list(r["survey"].columns) == ["survey", "column", "measure", "value"]


def test_repeated_calls_in_same_process_succeed(
    scenario1_path, resource_path, monkeypatch
):
    monkeypatch.chdir(scenario1_path.parent)
    r1 = om.run(path=str(scenario1_path), resource_path=resource_path)
    r2 = om.run(path=str(scenario1_path), resource_path=resource_path)
    assert (r1["survey"]["value"].to_numpy() == r2["survey"]["value"].to_numpy()).all()
