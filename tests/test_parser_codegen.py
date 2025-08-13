from pathlib import Path
from fort2py.fortran_parser import parse_sources
from fort2py.semantics import Semantics
from fort2py.codegen_python import generate_module

def test_parse_generate_basic(tmp_path: Path):
    src = tmp_path / "m.f90"
    src.write_text(\"\"\"module m
implicit none
contains
subroutine add_one(n)
  integer(kind=4), intent(inout) :: n
  n = n + 1
end subroutine
end module m
\"\"\")
    ir = parse_sources([src])
    Semantics(ir).analyze()
    mod = next(iter(ir.modules.values()))
    py = generate_module(mod)
    assert "def add_one" in py
    assert "Ref" in py  # because inout scalar requires Ref
