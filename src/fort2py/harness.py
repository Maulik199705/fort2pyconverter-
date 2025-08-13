from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional
import subprocess
import sys
import yaml
import json
import importlib.util
import numpy as np

from .utils import run_cmd, set_determinism_env


@dataclass
class SampleCase:
    name: str
    # For program runs:
    exe_args: List[str] = None
    stdin: Optional[str] = None
    cwd: Optional[str] = None
    # For function-level tests (optional future extension)
    module: Optional[str] = None
    function: Optional[str] = None
    inputs: Optional[Dict] = None


@dataclass
class VerificationConfig:
    # Points to a program/main in Fortran and its Python mirror module + entry function
    fortran_build_dir: Optional[str] = None
    fortran_exe: Optional[str] = None
    python_entry_module: Optional[str] = None
    python_entry_function: Optional[str] = None
    cases: List[SampleCase] = None

    @staticmethod
    def from_yaml(p: Path) -> "VerificationConfig":
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        cases = [SampleCase(**c) for c in data.get("cases", [])]
        return VerificationConfig(
            fortran_build_dir=data.get("fortran_build_dir"),
            fortran_exe=data.get("fortran_exe"),
            python_entry_module=data.get("python_entry_module"),
            python_entry_function=data.get("python_entry_function"),
            cases=cases,
        )


def _run_fortran(exe: Path, case: SampleCase) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(exe)] + (case.exe_args or []),
        input=(case.stdin or "").encode("utf-8") if case.stdin else None,
        cwd=case.cwd or None,
        capture_output=True,
        timeout=120,
    )


def _run_python(module_path: Path, func_name: str, case: SampleCase) -> str:
    # Dynamically import module and call function; case.inputs is dict of arguments
    spec = importlib.util.spec_from_file_location("entry_mod", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    fn = getattr(mod, func_name, None)
    if fn is None:
        raise RuntimeError(f"Python entry function not found: {func_name}")
    args = case.inputs or {}
    # Determinism
    np.random.seed(123456789)
    set_determinism_env()
    res = fn(**args)
    if isinstance(res, (bytes, bytearray)):
        return res.decode("utf-8", errors="ignore")
    if isinstance(res, (str,)):
        return res
    # Fallback to JSON
    try:
        return json.dumps(res, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    except Exception:
        return str(res)


def verify_equivalence(fort_src: Path, py_src: Path, cfg: VerificationConfig) -> bool:
    set_determinism_env()
    # Assumes fortran_exe prebuilt or built externally; building is separate step if desired
    for_exe = Path(cfg.fortran_exe) if cfg.fortran_exe else None
    if not for_exe or not for_exe.exists():
        raise RuntimeError("fortran_exe not provided or not found. Build it first.")
    py_entry = py_src / (cfg.python_entry_module + ".py")
    if not py_entry.exists():
        raise RuntimeError(f"Python entry module not found: {py_entry}")
    ok_all = True
    for case in cfg.cases or []:
        fort_run = _run_fortran(for_exe, case)
        fort_out = fort_run.stdout.decode("utf-8", errors="ignore")
        py_out = _run_python(py_entry, cfg.python_entry_function, case)
        if fort_out != py_out:
            sys.stderr.write(f"[Mismatch] case={case.name}\n--- Fortran ---\n{fort_out}\n--- Python ---\n{py_out}\n")
            ok_all = False
    return ok_all
