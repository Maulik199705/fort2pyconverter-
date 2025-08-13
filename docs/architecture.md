# Architecture

Components:
- Scanner: Recursively identifies Fortran source files.
- Parser: Conservative, line-oriented MVP that recognizes modules, subroutines, functions, programs, USE, basic declarations, and executable lines. Anything ambiguous or complex raises NotImplementedError.
- IR (Intermediate Representation): Dataclasses describing modules, program units, declarations, and arguments.
- Semantics: Enforces implicit none discipline, maps kinds to NumPy dtypes, annotates argument metadata (intent, byref, dims), collects migration notes.
- Codegen: Translates the IR into Python+NumPy modules. Uses Fortran-order arrays (order='F'), explicit pass-by-reference wrapper (Ref) for OUT/INOUT scalars, and deterministic intrinsics. I/O is intentionally not auto-translated in MVP to avoid silent format errors.
- Test Generator: Emits pytest smoke tests that instantiate arguments and call generated functions/subroutines deterministically.
- Verification Harness: Optionally compiles Fortran with gfortran and compares outputs against the Python translation for provided sample runs.
- Package Builder: Creates a Python package scaffold mirroring module names.
- GUI: Tkinter app to scan, convert, and view diffs with logs and progress.

Determinism:
- BLAS threads pinned (OpenBLAS/MKL/OMP).
- RNG seeded via intrinsics.random_seed or deterministic default.
- Explicit failures prevent silent differences.

Guardrails:
- Any unsupported construct raises NotImplementedError with a clear message.
- No TODOs or stubs are emitted; migration notes document fallbacks (e.g., kind fallback to float64).

Extensibility roadmap:
- Introduce a robust expression parser and full AST-based translator.
- Add FORMAT I/O parsing and mapping to Python format specifications.
- Handle module variables (SAVE), derived types, pointers/allocatables, interfaces, and advanced control flow (select case, where, forall, do concurrent).
- Support COMMON/EQUIVALENCE under strict safety rules (numpy views or explicit errors).
- Add Numba paths for hot loops.
