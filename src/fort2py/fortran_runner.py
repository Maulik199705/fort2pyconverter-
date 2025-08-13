from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import shutil

from .utils import run_cmd


def compile_and_run_project(src_dir: Path, output_exe: Path, sources: Optional[List[Path]] = None, extra_flags: Optional[List[str]] = None):
    if shutil.which("gfortran") is None:
        raise RuntimeError("gfortran not found in PATH; required for verification harness.")
    if sources is None:
        sources = list(src_dir.rglob("*.f90"))
    cmd = ["gfortran", "-O2", "-fimplicit-none", "-o", str(output_exe)] + [str(s) for s in sources]
    if extra_flags:
        cmd.extend(extra_flags)
    run_cmd(cmd, cwd=src_dir)
    return output_exe
