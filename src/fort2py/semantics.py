from __future__ import annotations
from typing import Dict, Tuple
from .ir import ProjectIR, VarDecl, Subroutine, Function
from .types import DTYPE_MAP


class Semantics:
    def __init__(self, ir: ProjectIR):
        self.ir = ir
        self.migration_notes: Dict[str, str] = {}

    def analyze(self):
        # Validate implicit none by requiring declarations for all variables referenced.
        # MVP: assume implicit none present; deeper analysis would require full symbol resolution.
        # Validate kinds and map to numpy dtypes.
        for mod in self.ir.modules.values():
            for sub in mod.subroutines:
                self._annotate_args_from_decls(sub)
                self._validate_decls(sub)
            for fun in mod.functions:
                self._annotate_args_from_decls(fun)
                self._validate_decls(fun)

    def _validate_decls(self, unit):
        for d in unit.declarations:
            if d.type_spec not in ("real", "integer", "logical", "character"):
                raise NotImplementedError(f"Type not supported in MVP: {d.type_spec}")
            # Validate kind mapping exists
            if d.type_spec == "real":
                _ = DTYPE_MAP.real_from_kind(d.kind)
            elif d.type_spec == "integer":
                _ = DTYPE_MAP.int_from_kind(d.kind)
            elif d.type_spec == "logical":
                # map to bool
                pass
            elif d.type_spec == "character":
                # map to Python str; char arrays not robustly supported in MVP
                if d.dims:
                    raise NotImplementedError("CHARACTER arrays unsupported in MVP.")
        # Migration notes could be extended here

    def _annotate_args_from_decls(self, unit: Subroutine | Function):
        declmap: Dict[str, VarDecl] = {d.name.lower(): d for d in unit.declarations}
        for a in unit.args:
            v = declmap.get(a.name.lower())
            if v:
                a.intent = v.intent
                a.type_spec = v.type_spec
                a.kind = v.kind
                a.dims = v.dims
                # If scalar and intent out/inout, enforce byref for Python
                a.byref = (a.dims is None) and (a.intent in ("out", "inout"))
            else:
                # Without explicit declaration in MVP, we bail to avoid implicit typing
                raise NotImplementedError(f"Argument '{a.name}' lacks explicit declaration (implicit none required).")
