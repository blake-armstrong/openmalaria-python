# openmalaria (Python bindings)

Python bindings for [OpenMalaria](https://github.com/SwissTPH/openmalaria),
built with [nanobind](https://github.com/wjakob/nanobind). Runs a scenario in a
fresh subprocess per call (see "Why a subprocess per run()" below) and returns
pandas DataFrames directly

## Install

This repo depends on the
[openmalaria](https://github.com/blake-armstrong/openmalaria) C++ core as a git
submodule (`core/`), which is not python-aware. The `OM_BUILD_PYTHON` CMake flag
is built from a local patch here (see `patches/`)

```sh
git submodule update --init
git -C core apply ../patches/0001-add-python-bindings-hook.patch
pip install .
```

(editable, for development: `pip install -e .`)

With [uv](https://docs.astral.sh/uv/):

```sh
git submodule update --init
git -C core apply ../patches/0001-add-python-bindings-hook.patch
uv venv
uv pip install .
```

(editable: `uv pip install -e .`)

If `core/CMakeLists.txt` changes upstream in a way that conflicts with the
patch, re-run `git -C core apply` after resolving and update the patch file
(`git -C core diff > patches/0001-add-python-bindings-hook.patch`).

## Usage

```python
import openmalaria as om

result = om.run(path="scenario.xml")
result["survey"]       # pd.DataFrame: survey, column, measure, value
result["continuous"]   # pd.DataFrame (one row per timestep) or None
```

Or pass scenario XML content directly instead of a file path:

```python
result = om.run(xml=scenario_xml_string, resource_path="/path/to/resources")
```

NB: schema lookup resolves relative to the current working directory for both
`path=` and `xml=` (not relative to the scenario file's own directory, if using
`path=`). Run from a directory containing `scenario_current.xsd`, or otherwise
ensure the schema is discoverable from the working directory.

`om.run()` also accepts `validate_only=True` (parse/validate the scenario and
stop before any timestep evolution. This acts as a cheap sanity check,
equivalent to the CLI's `--validate-only`), `seed=<int>` (override the
scenario's `@iseed`), and `verbose=True`/`progress=True` (equivalent to the CLI
flags of the same name).

### `survey` DataFrame schema

Mirrors `output.txt`'s own row schema exactly: `survey` (1-based survey number),
`column` (encodes age-group/cohort/species/genotype/drug the same way
`output.txt` does), `measure` (the OutMeasure id), `value`.

### `continuous` DataFrame schema

One row per reported timestep, one column per enabled `monitoring/continuous`
metric (column names taken from the scenario's own metric titles). `None` if the
scenario has no `<continuous>` monitoring configured.

## Version info

```python
>>> om.version()
{'program_version': 'schema-50.0', 'schema_version': 50}
```

Equivalent to the CLI's `openMalaria --version`.

## IMPORTATNT: one subprocess per run()

OpenMalaria's C++ core keeps several pieces of state as process-global statics
that `init()` functions populate but never clear. This works for the CLI (always
exactly one process per scenario), but not for a library function callers might
invoke repeatedly in one long-lived process. Verified examples:

- `util::CommandLine::resourcePath` -- a 2nd call with `resource_path` set
  throws outright ("--resource-path (or -p) may only be given once").
- `util::CommandLine::options` -- boolean CLI flags (`verbose`, `progress`, ...)
  leak silently across calls; once set, stuck on for the rest of the process.
- `interventions::InterventionManager` -- append-only; throws on a 2nd run
  reusing any `<component id="...">` name, and silently duplicates/accumulates
  timed and continuous deployments otherwise.
- `Transmission::PerHostAnophParams::params` -- append-only per mosquito
  species; a 2nd run's species indices land on the *first* run's leftover
  entries, silently using the wrong entomological parameters.
- `mon::Continuous::toReport` -- append-only; a 2nd run's `continuous` DataFrame
  would include the first run's columns mixed into its own.
- `mon::internal::runtime.conditions` -- push_back-only, never cleared.

It would be ideal to fix the underyling issues with OpenMalaria, but I am not an
admin there. So instead, a work around is to launch
`python -m openmalaria._worker` fresh for every call, so there's never a second
call in the same still-alive process for any of the above to leak across.

It costs a process-spawn + reimport per `run()` call

## Parallelism (mpi4py)

`run()`'s own subprocess isolation makes it safe to call repeatedly in one
process, but that's still one scenario at a time. For genuine parallelism across
scenarios (especially across nodes on a cluster), distribute with mpi4py:

```python
from mpi4py import MPI
import openmalaria as om

comm = MPI.COMM_WORLD
scenario_paths = [...]  # one per rank, or distribute a longer list up front

result = om.run(path=scenario_paths[comm.rank])
```

Pin ranks to individual cores via your launcher, e.g.
`mpirun --bind-to core -np N python script.py`. Note each rank's `run()` call
still spawns its own worker subprocess underneath

## Tests

```sh
uv run --extra test pytest
```

## Limitations

**No checkpoint/resume support.** Checkpointing (`-c`/`--checkpoint-file` on the
CLI) remains a CLI-only feature; `om.run()` exposes no checkpoint parameters.

**CPU-core pinning is the caller's responsibility.** OpenMalaria's simulation
engine has no internal threading (no OpenMP, no `std::thread` anywhere in the
C++ core), so single-core execution is achieved externally:
`mpirun --bind-to core -np N python script.py`, or
`os.sched_setaffinity(0, {core_id})` (Linux) at the start of a worker process.
