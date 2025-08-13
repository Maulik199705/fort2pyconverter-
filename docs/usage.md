# Usage

CLI:
- Scan:
  fort2py scan --path /path/to/repo --include-legacy
- Convert:
  fort2py convert --path /path/to/repo --out build/python_out
- Build package:
  fort2py build-package --in build/python_out --name mypkg --out build/pkg_out
- Verify (requires gfortran and a sample config):
  fort2py verify --fort-src /path/to/repo --py-src build/python_out --sample-config samples/run.yaml

GUI:
- fort2py gui
- Choose local folder, Scan, then Convert. Use "Show Diff" to see a unified diff of first module.

Notes:
- The MVP requires explicit declarations (implicit none) and literal array dimensions.
- OUT/INOUT scalar arguments must be passed as fort2py.types.Ref.
- Arrays are created Fortran-ordered (order='F'), facilitating column-major compatibility.
