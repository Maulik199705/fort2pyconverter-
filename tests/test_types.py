import numpy as np
from fort2py.types import DTYPE_MAP, Ref, as_fortran_array

def test_kind_map():
    assert DTYPE_MAP.real_from_kind(4) == np.float32
    assert DTYPE_MAP.real_from_kind(8) == np.float64
    assert DTYPE_MAP.int_from_kind(4) == np.int32
    assert DTYPE_MAP.int_from_kind(8) == np.int64

def test_ref():
    x = Ref(1)
    assert x.v == 1
    x.v = 5
    assert x.v == 5

def test_as_fortran_array():
    a = as_fortran_array((2,3), np.float64)
    assert a.flags["F_CONTIGUOUS"]
