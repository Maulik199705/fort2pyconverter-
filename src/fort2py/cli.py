import argparse
import sys
from pathlib import Path

from .scanner import scan_fortran_files
from .converter import convert_project
from .package_builder import build_python_package
from .harness import VerificationConfig, verify_equivalence
from .fortran_runner import compile_and_run_project
from .utils import set_determinism_env
from .gui_app import launch_gui


def main():
    parser = argparse.ArgumentParser(prog="fort2py", description="Fortran to Python+NumPy translator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="Scan a local folder for Fortran files")
    p_scan.add_argument("--path", type=str, required=True)
    p_scan.add_argument("--include-legacy", action="store_true", help="Include .f, .for files")

    p_convert = sub.add_parser("convert", help="Convert a Fortran project to Python")
    p_convert.add_argument("--path", type=str, required=True)
    p_convert.add_argument("--out", type=str, required=True)
    p_convert.add_argument("--include-legacy", action="store_true")
    p_convert.add_argument("--fail-on-unsupported", action="store_true", help="Stop on first unsupported construct")

    p_build = sub.add_parser("build-package", help="Create a Python package from generated sources")
    p_build.add_argument("--in", dest="in_dir", type=str, required=True)
    p_build.add_argument("--name", type=str, required=True)
    p_build.add_argument("--out", type=str, default="build/pkg_out")

    p_verify = sub.add_parser("verify", help="Run verification harness against sample runs")
    p_verify.add_argument("--fort-src", type=str, required=True)
    p_verify.add_argument("--py-src", type=str, required=True)
    p_verify.add_argument("--sample-config", type=str, required=True)

    p_gui = sub.add_parser("gui", help="Launch GUI")
    args = parser.parse_args()

    set_determinism_env()

    if args.cmd == "scan":
        files = scan_fortran_files(Path(args.path), include_legacy=args.include_legacy)
        for f in files:
            print(f)
        print(f"Found {len(files)} Fortran files")
    elif args.cmd == "convert":
        files = scan_fortran_files(Path(args.path), include_legacy=args.include_legacy)
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        convert_project(files, out_dir, fail_on_unsupported=args.fail_on_unsupported)
        print(f"Conversion complete. Output: {out_dir}")
    elif args.cmd == "build-package":
        in_dir = Path(args.in_dir)
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        build_python_package(in_dir, out_dir, args.name)
        print(f"Package scaffold created: {out_dir}")
    elif args.cmd == "verify":
        cfg = VerificationConfig.from_yaml(Path(args.sample_config))
        ok = verify_equivalence(Path(args.fort_src), Path(args.py_src), cfg)
        sys.exit(0 if ok else 1)
    elif args.cmd == "gui":
        launch_gui()
