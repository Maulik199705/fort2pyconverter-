from pathlib import Path
from typing import List


FORTRAN_EXTS = {".f90", ".f95"}
FORTRAN_LEGACY_EXTS = {".f", ".for"}


def scan_fortran_files(root: Path, include_legacy: bool = False) -> List[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")
    exts = set(FORTRAN_EXTS)
    if include_legacy:
        exts |= FORTRAN_LEGACY_EXTS
    found: List[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            found.append(p)
    found.sort()
    return found
