# Migration Notes Template

- Indexing:
  Fortran is 1-based; Python is 0-based. fort2py uses Fortran-order arrays and attempts to preserve semantics, but index expressions in executable statements are not rewritten in MVP. Review and adjust if needed.
- Pass-by-reference:
  Scalar OUT/INOUT arguments must be wrapped in fort2py.types.Ref in Python.
- Types:
  REAL/INTEGER kinds map to NumPy dtypes; see docs/limitations.md for fallbacks.
- I/O:
  FORMAT and file I/O not auto-translated in MVP. Implement equivalent Python I/O manually, or extend the converter.
- Global state:
  Module variables (SAVE) not supported in MVP; refactor into explicit state passing where needed.
