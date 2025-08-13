# Limitations (MVP)

- Parsing is conservative and line-oriented; complex syntax, continuation lines with advanced constructs, preprocessor directives, and many F2003+ features are not handled yet.
- FORMAT/READ/WRITE/OPEN/CLOSE/REWIND translation is not included to avoid silent format mismatches. Explicitly raises NotImplementedError when encountered.
- GOTO/COMPUTED GOTO not supported.
- COMMON/EQUIVALENCE not supported.
- Module variables (SAVE) are not translated in MVP to avoid global mutable state issues.
- CHARACTER arrays unsupported; scalar CHARACTER maps to Python str.
- Non-literal array dimensions unsupported; assumed-shape and deferred-shape arrays not handled.
- Derived types and interfaces are placeholders for future expansion.
- REAL(kind=10/16) may fall back to float64 if float128 unavailable. INTEGER(kind=16) falls back to int64.
- No paid APIs are used; open-source compiler (gfortran) is optional for verification harness.
