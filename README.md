# openmalaria-tools

Helpers for analysing [OpenMalaria](https://github.com/SwissTPH/openmalaria)
output from Python.

Running scenarios is done by the `openmalaria` package itself
([openmalaria-nanobind](https://github.com/blake-armstrong/openmalaria-nanobind),
the minimal compiled bindings): `import openmalaria as om; om.run(...)`.
Building, the one-subprocess-per-`run()` isolation, and the
`survey`/`continuous` DataFrame schemas are all documented there.

This package adds small, thin helpers over what `om.run()` returns, with no
calibration or workflow logic: `openmalaria_tools.survey`,
`openmalaria_tools.scenario` and `openmalaria_tools.metrics`.

## Install

```sh
pip install openmalaria-tools
```

This pulls in `openmalaria` (prebuilt wheels). For development against a local
checkout of both repos side by side:

```sh
uv sync
```

`[tool.uv.sources]` in `pyproject.toml` points `openmalaria` at
`../openmalaria-nanobind` (editable). Use `uv sync --no-sources` to take it from
PyPI instead.

## Usage

```python
import openmalaria as om
from openmalaria_tools import metrics, scenario, survey

result = om.run(xml=scenario_xml, resource_path="resources", schema_dir="schema")
df = result["survey"]

survey.by_age_group(df, "nHost")  # (age group x survey) array
metrics.prevalence(df)  # nPatent / nHost, (age group x survey)
metrics.rate_by_age_group(df, "nUncomp")  # measure / nHost
metrics.total_rate(df, "expectedSevere")  # per survey, all ages pooled

upperbounds = scenario.age_group_upperbounds(scenario_xml)
metrics.pfpr(df, upperbounds, lo=2, hi=10)  # PfPR_2-10 at the last survey
```

### `openmalaria_tools.survey`

- `by_age_group(survey, measure)`: values of one measure as an
  (age group x survey) array. `measure` is a `MEASURE_CODES` name or its integer
  code.
- `age_groups(survey)` / `n_age_groups(survey)`: the monitoring age-group
  columns present.
- `read_output_txt(path)`: read an OpenMalaria CLI `output.txt` into the same
  DataFrame schema as `run()["survey"]`, for comparing CLI and Python runs.

### `openmalaria_tools.scenario`

- `age_group_bounds(xml)`: monitoring age-group edges
  `[lowerbound, upperbound_1, ..., upperbound_n]`.
- `age_group_upperbounds(xml)`, `age_group_midpoints(xml)`.
- `age_group_labels(upperbounds, lowerbound=0.0)`: `"0-0.5"`, `"0.5-1"`, ...

### `openmalaria_tools.metrics`

- `prevalence(survey)`, `rate_by_age_group(survey, measure)`: per age group and
  survey, divided by `nHost`. Division by zero gives `nan`/`inf`, not an error.
- `total_rate(survey, measure)`: per survey, summed over age groups.
- `pfpr(survey, upperbounds, lo=2, hi=10, survey_index=-1)`: parasite
  prevalence over the monitoring age groups lying entirely within `[lo, hi]`.

`ScenarioResult` (an `OMRunResult` with a `name`) is also available for callers
batching many runs.

## Parallelism (mpi4py)

`run()`'s own subprocess isolation makes it safe to call repeatedly in one
process, but that's still one scenario at a time. For genuine parallelism across
scenarios (especially across nodes on a cluster), distribute with mpi4py
(`pip install "openmalaria-tools[mpi]"`):

```python
from mpi4py import MPI
import openmalaria as om

comm = MPI.COMM_WORLD
scenario_paths = [...]  # one per rank, or distribute a longer list up front

result = om.run(path=scenario_paths[comm.rank])
```

Pin ranks to individual cores via your launcher, e.g.
`mpirun --bind-to core -np N python script.py`. Note each rank's `run()` call
still spawns its own worker subprocess underneath.

## Development

```sh
uv run pytest
uv run ruff format --check
uv run ruff check
uv run basedpyright
```
