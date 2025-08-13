from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal, Tuple
import numpy as np


RealKind = Literal[2, 4, 8, 10, 16]
IntKind = Literal[1, 2, 4, 8, 16]


@dataclass(frozen=True)
class DTypeMap:
    default_real: np.dtype = np.float64
    default_int: np.dtype = np.int32

    def real_from_kind(self, kind: Optional[int]) -> np.dtype:
        if kind is None:
            return self.default_real
        # Common mapping. If project uses nonstandard kinds, we will raise in semantics if ambiguous.
        match kind:
            case 2:
                return np.float16
            case 4:
                return np.float32
            case 8:
                return np.float64
            case 10 | 16:
                # NumPy float128 availability varies by platform. Use float64 + migration note fallback.
                try:
                    return np.float128  # type: ignore[attr-defined]
                except Exception:
                    return np.float64
            case _:
                raise ValueError(f"Unsupported REAL kind={kind}")
    
    def int_from_kind(self, kind: Optional[int]) -> np.dtype:
        if kind is None:
            return self.default_int
        match kind:
            case 1:
                return np.int8
            case 2:
                return np.int16
            case 4:
                return np.int32
            case 8:
                return np.int64
            case 16:
                # Not standard in NumPy; degrade with migration note.
                return np.int64
            case _:
                raise ValueError(f"Unsupported INTEGER kind={kind}")


DTYPE_MAP = DTypeMap()


def as_fortran_array(shape: Tuple[int, ...], dtype: np.dtype, fill=0):
    # Always use Fortran-order to align with column-major layout.
    return np.full(shape, fill_value=fill, dtype=dtype, order="F")


class Ref:
    """
    Pass-by-reference wrapper for scalars.
    Usage: x = Ref(0.0); subroutine(x); print(x.v)
    """
    __slots__ = ("v",)
    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return f"Ref({self.v!r})"
