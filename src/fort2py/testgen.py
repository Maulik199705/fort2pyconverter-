from __future__ import annotations
from pathlib import Path
from typing import List
from .ir import ProjectIR, Module
from .utils import write_text


PYTEST_HEADER = """# Auto-generated tests by fort2py
import numpy as np
import pytest
from fort2py.types import Ref
from fort2py.intrinsics import *
"""


def generate_unit_tests(ir: ProjectIR, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for mod in ir.modules.values():
        lines = [PYTEST_HEADER]
        lines.append(f"import {mod.name.lower()} as m")
        # Simple smoke tests: ensure functions/subroutines are callable with default placeholders
        for sub in mod.subroutines:
            args = []
            for a in sub.args:
                if a.dims:
                    shape = ", ".join(str(d) for d in a.dims)
                    dt = "np.float64" if (a.type_spec or "real") == "real" else "np.int32"
                    args.append(f"np.zeros(({shape},), dtype={dt}, order='F')")
                else:
                    if a.byref:
                        args.append("Ref(0)")
                    else:
                        args.append("0")
            lines.append(f"def test_{mod.name.lower()}_{sub.name}():")
            lines.append(f"    m.{sub.name}({', '.join(args)})")
            lines.append("")
        write_text(out_dir / f"test_{mod.name.lower()}.py", "\n".join(lines))
