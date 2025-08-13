# fort2py

A deterministic, test-driven MVP desktop app and library to translate Fortran (F90/F95/F2003+) code to semantically-equivalent Python+NumPy, with automated unit/regression tests, a verification harness, and a Tkinter GUI.

Features:
- Recursively finds Fortran files (.f90, optional .f, .for, .f95)
- Builds project-level context (modules, uses, interfaces, derived types)
- Context-aware line-by-line translation to Python (no silent stubs)
- Pure Python + NumPy output, optional Numba hooks left off by default
- Auto-generates tests from detected I/O and provided sample runs
- GUI with progress, diff viewer, and error logs
- Clean, runnable Python packages mirroring Fortran module structure
- Verification harness: compares Fortran vs Python outputs deterministically
- Strict guardrails: no TODOs, explicit NotImplementedError on unsupported features
- Migration notes for unavoidable semantic differences

Quickstart:
1) Install:
   - Python 3.9+
   - pip install -e ".[dev]"
   - Optional: gfortran in PATH for verification harness.

2) Run GUI:
   - fort2py gui

3) CLI basics:
   - fort2py scan --path /path/to/repo
   - fort2py convert --path /path/to/repo --out build/python_out
   - fort2py build-package --in build/python_out --name mypkg
   - fort2py verify --fort-src /path/to/repo --py-src build/python_out --sample-config samples/run.yaml

Determinism:
- Seeds and BLAS threading pinned (OpenBLAS/MKL/OMP set to 1).
- Random generators seeded in both Fortran (if detected) and Python shims.
- Differences documented in docs/limitations.md.

Documentation:
- See docs/architecture.md, docs/usage.md, docs/limitations.md, docs/migration_notes_template.md

License: MIT
