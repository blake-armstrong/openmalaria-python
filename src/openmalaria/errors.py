from __future__ import annotations


class OpenMalariaError(Exception):
    """Raised when the OpenMalaria C++ core fails during a run (invalid
    scenario, XSD/schema error, command-line/config error)."""
