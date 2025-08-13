from __future__ import annotations
from pathlib import Path
from typing import List
import shutil

from .utils import write_text


SETUP_PY_TPL = """from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["numpy>=1.25"],
)
"""


def build_python_package(in_dir: Path, out_dir: Path, name: str):
    pkg_dir = out_dir / name
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / name).mkdir(parents=True, exist_ok=True)
    # Copy modules
    for p in in_dir.glob("*.py"):
        shutil.copy2(p, pkg_dir / name / p.name)
    # __init__
    write_text(pkg_dir / name / "__init__.py", "")
    # setup.py
    write_text(pkg_dir / "setup.py", SETUP_PY_TPL.format(name=name))
