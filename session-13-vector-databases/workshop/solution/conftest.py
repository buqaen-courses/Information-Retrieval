"""Pytest configuration for the Session 13 solution tests.

The course repo has a `datasets/` folder that holds generated data. It has no
`__init__.py`, so Python happily treats it as a *namespace package* named
`datasets`. LanceDB's optional HuggingFace-`datasets` support does
`from datasets import Dataset`, and when the test process has our folder on
sys.path it finds the namespace package instead, which has no `Dataset`, and
raises ImportError.

This file makes the collision impossible: it removes the repo root from the
front of sys.path before any test imports LanceDB, and drops a `datasets`
namespace package from sys.modules if pytest already imported one. The real
HuggingFace `datasets` package (installed in the course venv) still imports
normally, because it lives in site-packages.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# Put site-packages first so the real `datasets` wins over our data folder.
for _entry in [str(ROOT)]:
    if _entry in sys.path:
        sys.path.remove(_entry)

# If pytest already imported our namespace `datasets`, forget it.
_ns = sys.modules.get("datasets")
if _ns is not None and getattr(_ns, "__file__", None) is None:
    del sys.modules["datasets"]