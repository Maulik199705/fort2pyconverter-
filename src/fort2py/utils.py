from __future__ import annotations
import difflib
import json
import os
import subprocess
from pathlib import Path
from typing import Iterable, List, Optional


def set_determinism_env():
    # Pin BLAS/threads for determinism
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    # Ensure Python hash seeds fixed for deterministic dict ordering between runs
    os.environ.setdefault("PYTHONHASHSEED", "0")


def run_cmd(cmd: List[str], cwd: Optional[Path] = None, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True, capture_output=True, text=True, timeout=timeout)


def require(cond: bool, msg: str):
    if not cond:
        raise AssertionError(msg)


def diff_text(a: str, b: str, fromfile: str = "from", tofile: str = "to") -> str:
    return "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile=fromfile, tofile=tofile))


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write_text(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def deterministic_rng(seed: Optional[int] = None):
    import numpy as np
    s = 123456789 if seed is None else int(seed)
    return np.random.default_rng(s)
