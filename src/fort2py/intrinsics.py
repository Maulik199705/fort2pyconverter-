from __future__ import annotations
import math
from typing import Any, Optional, Tuple
import numpy as np

from .utils import require, deterministic_rng


def present(x: Optional[Any]) -> bool:
    return x is not None


def lbound(a: np.ndarray, dim: Optional[int] = None) -> Any:
    if dim is None:
        return np.array([1 for _ in a.shape], dtype=np.int64)
    require(1 <= dim <= a.ndim, f"lbound: dim out of range: {dim}")
    return 1


def ubound(a: np.ndarray, dim: Optional[int] = None) -> Any:
    if dim is None:
        return np.array([n for n in a.shape], dtype=np.int64)
    require(1 <= dim <= a.ndim, f"ubound: dim out of range: {dim}")
    return a.shape[dim - 1]


def size(a: np.ndarray, dim: Optional[int] = None) -> int:
    if dim is None:
        return a.size
    require(1 <= dim <= a.ndim, f"size: dim out of range: {dim}")
    return a.shape[dim - 1]


def shape(a: np.ndarray) -> Tuple[int, ...]:
    return a.shape


def matmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    # Fortran matmul is column-major; data is F-ordered; np.matmul suffices.
    return a @ b


def dot_product(a: np.ndarray, b: np.ndarray) -> Any:
    return np.vdot(a, b)


def transpose(a: np.ndarray) -> np.ndarray:
    return np.swapaxes(a, -2, -1)


def merge(tsrc, fsrc, mask):
    return np.where(mask, tsrc, fsrc)


def sign(a, b):
    return math.copysign(abs(a), b)


def random_seed(seed: Optional[int] = None):
    # Set deterministic RNG via numpy RNG
    rng = deterministic_rng(seed)
    np.random.seed(rng.integers(0, 2**31 - 1))


def random_number(a: np.ndarray):
    # Fill array in place using deterministic seed set earlier
    a[...] = np.random.random_sample(size=a.shape)


def nint(x):
    return np.rint(x).astype(int)


def modulo(a, p):
    return a - p * np.floor(a / p)


def allocated(x) -> bool:
    return x is not None


def associated(x) -> bool:
    return x is not None
