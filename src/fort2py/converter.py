from __future__ import annotations
from pathlib import Path
from typing import List

from .fortran_parser import parse_sources
from .semantics import Semantics
from .codegen_python import write_project_python
from .migration_notes import write_migration_notes


def convert_project(files: List[Path], out_dir: Path, fail_on_unsupported: bool = False):
    # Parse
    ir = parse_sources(files)
    # Analyze semantics
    sema = Semantics(ir)
    sema.analyze()
    # Codegen
    written = write_project_python(ir, out_dir)
    # Migration notes
    write_migration_notes(sema, out_dir)
    return written
