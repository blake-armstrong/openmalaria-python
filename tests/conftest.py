from __future__ import annotations

import shutil
from pathlib import Path

import pytest

SCHEMA_VERSION = 50

REPO_ROOT = Path(__file__).resolve().parents[1]
CORE_DIR = REPO_ROOT / "core"
CORE_TEST_DIR = CORE_DIR / "test"
RESOURCE_DIR = CORE_TEST_DIR
EXPECTED_DIR = CORE_TEST_DIR / "expected"
SCHEMA_FILE = CORE_DIR / "schema" / f"scenario_{SCHEMA_VERSION}.xsd"


@pytest.fixture(scope="session")
def resource_path() -> str:
    return str(RESOURCE_DIR)


@pytest.fixture
def scenario1_path(tmp_path: Path) -> Path:
    shutil.copy(SCHEMA_FILE, tmp_path / "scenario_current.xsd")
    dest = tmp_path / "scenario1.xml"
    shutil.copy(CORE_TEST_DIR / "scenario1.xml", dest)
    return dest


@pytest.fixture(scope="session")
def scenario1_result(tmp_path_factory, resource_path):
    import os

    import openmalaria as om

    sim_dir = tmp_path_factory.mktemp("sim")
    shutil.copy(SCHEMA_FILE, sim_dir / "scenario_current.xsd")
    scenario_path = sim_dir / "scenario1.xml"
    shutil.copy(CORE_TEST_DIR / "scenario1.xml", scenario_path)

    old_cwd = os.getcwd()
    os.chdir(sim_dir)
    try:
        return om.run(path=str(scenario_path), resource_path=resource_path)
    finally:
        os.chdir(old_cwd)


@pytest.fixture
def expected_output1() -> Path:
    return EXPECTED_DIR / "output1.txt"


@pytest.fixture
def expected_ctsout1() -> Path:
    return EXPECTED_DIR / "ctsout1.txt"
