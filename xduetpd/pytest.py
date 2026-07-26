"""Tiny local pytest-compatible shim for environments without pytest.

It supports the subset this repo needs: importing files passed on the command
line and running zero-argument functions named test_*.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import traceback


def _load_module(path: pathlib.Path):
    name = "local_pytest_" + path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    files = [pathlib.Path(arg) for arg in argv if arg.endswith(".py")]
    if not files:
        files = list(pathlib.Path("tests").glob("test_*.py"))
    failed = 0
    passed = 0
    for path in files:
        module = _load_module(path)
        for name in sorted(dir(module)):
            if not name.startswith("test_"):
                continue
            obj = getattr(module, name)
            if not callable(obj):
                continue
            try:
                obj()
            except Exception:
                failed += 1
                print(f"{path}::{name} FAILED")
                traceback.print_exc()
            else:
                passed += 1
                print(f"{path}::{name} PASSED")
    print(f"{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
