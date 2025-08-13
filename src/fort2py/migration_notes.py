from __future__ import annotations
from pathlib import Path
from .semantics import Semantics
from .utils import write_text

TEMPLATE = """Migration Notes (auto-generated)

Scope:
- 1-based Fortran indices require care; MVP uses Fortran-order arrays but does not rewrite every index.
- Scalars with INTENT(OUT/INOUT) must be passed as fort2py.types.Ref instances.
- CHARACTER arrays unsupported in MVP.
- Module variables (global SAVE) unsupported in MVP.
- Complex I/O with FORMAT/READ/WRITE not supported in MVP; explicit failure triggered.
- Non-literal dimensions and assumed-shape arrays not supported in MVP.
- Preprocessor directives are unsupported.
- EQUIVALENCE/COMMON not supported in MVP; explicit failure would occur if parsed.
- GOTO/COMPUTED GOTO not supported in MVP.

Determinism:
- BLAS threads pinned to 1 via env.
- numpy.random seeded via intrinsics.random_seed or deterministic default.

Known semantic differences:
- Potential fallback from REAL(kind=10/16) to float64 if float128 unavailable.
- INTEGER(kind=16) falls back to int64.

Additional notes from analysis:
{notes}
"""


def write_migration_notes(sema: Semantics, out_dir: Path):
    notes = "\n".join(f"- {k}: {v}" for k, v in sema.migration_notes.items())
    text = TEMPLATE.format(notes=notes if notes else "- None")
    write_text(out_dir / "MIGRATION_NOTES.txt", text)
