import numpy as np
from fort2py.intrinsics import lbound, ubound, size, shape, matmul, dot_product, merge, sign, random_seed, random_number

def test_bounds():
    a = np.zeros((3,4), order="F")
    assert (lbound(a) == np.array([1,1])).all()
    assert ubound(a, 1) == 3
    assert size(a, 2) == 4

def test_random():
    random_seed(123)
    a = np.empty((2,2))
    random_number(a)
    b = a.copy()
    random_seed(123)
    c = np.empty((2,2))
    random_number(c)
    assert np.allclose(b, c)
