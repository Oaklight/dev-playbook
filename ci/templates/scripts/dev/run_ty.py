#!/usr/bin/env python3
"""Run ``ty check`` against this checkout's own sources, in any worktree (stdlib only).

CI installs the project editable from its own checkout, so ``ty`` resolves the
project's packages to the sources under test.  A local environment may hold an
editable install that points at ANOTHER checkout (for example the main checkout
while you work in a git worktree).  ``ty`` then type-checks this checkout's
tests against the other checkout's sources and reports spurious diagnostics.

This wrapper puts this checkout's ``src`` directories first with
``--extra-search-path`` and points ``ty`` at the active environment with
``--python``, so the result is the same from every worktree.  Extra arguments
go to ``ty check``.  Exit status is ``ty``'s.

The ``src`` directories are discovered, not hard-coded: every directory named
``src`` up to three levels below the repository root that holds a Python
package or module (``src``, ``packages/*/src``, ...).  Set
``RUN_TY_SEARCH_PATHS`` to a ``os.pathsep``-separated list of directories
(relative to the repository root) to replace the discovery.

Usage::

    python scripts/dev/run_ty.py [ty check arguments]
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

SEARCH_PATHS_ENV = "RUN_TY_SEARCH_PATHS"
MAX_DEPTH = 3
SKIP_DIRS = frozenset(
    {
        "node_modules",
        "site-packages",
        "build",
        "dist",
        "venv",
        "env",
        "__pycache__",
    }
)


def find_repo_root(start: Path) -> Path | None:
    """Return the repository root above ``start``.

    A git checkout or worktree has ``.git`` (a directory, or a file in a
    worktree).  Without one, the nearest ancestor with a ``pyproject.toml``.
    """
    for marker in (".git", "pyproject.toml"):
        for p in (start, *start.parents):
            if (p / marker).exists():
                return p
    return None


def _holds_python(src: Path) -> bool:
    """Return whether ``src`` holds a package directory or a top-level module."""
    for child in src.iterdir():
        if child.is_dir() and (child / "__init__.py").is_file():
            return True
        if child.is_file() and child.suffix == ".py":
            return True
    return False


def discover_search_paths(root: Path) -> list[Path]:
    """Return the ``src`` directories of the checkout, shallowest first.

    Hidden directories, virtual environments and build output are skipped.
    """
    found: list[Path] = []

    def walk(directory: Path, depth: int) -> None:
        for child in sorted(directory.iterdir()):
            if not child.is_dir() or child.is_symlink():
                continue
            name = child.name
            if name.startswith(".") or name in SKIP_DIRS or name.endswith(".egg-info"):
                continue
            if (child / "pyvenv.cfg").is_file():
                continue
            if name == "src" and _holds_python(child):
                found.append(child)
            elif depth < MAX_DEPTH:
                walk(child, depth + 1)

    walk(root, 1)
    return sorted(found, key=lambda p: (len(p.relative_to(root).parts), str(p)))


def search_paths(root: Path) -> list[Path]:
    """Return the search paths: ``RUN_TY_SEARCH_PATHS`` if set, else discovery."""
    override = os.environ.get(SEARCH_PATHS_ENV)
    if override:
        return [root / p for p in override.split(os.pathsep) if p]
    return discover_search_paths(root)


def pick_python() -> str:
    """Return the environment prefix: $VIRTUAL_ENV, $CONDA_PREFIX, sys.prefix."""
    return os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX") or sys.prefix


def find_ty() -> list[str] | None:
    """Locate ``ty`` on PATH, beside this interpreter, or as ``python -m ty``."""
    exe = shutil.which("ty")
    if exe:
        return [exe]
    sibling = Path(sys.executable).with_name("ty")
    if sibling.exists():
        return [str(sibling)]
    probe = subprocess.run(
        [sys.executable, "-m", "ty", "--version"], capture_output=True, text=True
    )
    return [sys.executable, "-m", "ty"] if probe.returncode == 0 else None


def main(argv: list[str]) -> int:
    """Run ``ty check`` with this checkout's sources first on the search path."""
    root = find_repo_root(Path.cwd())
    if root is None:
        print("run_ty: run from inside a git checkout.", file=sys.stderr)
        return 2
    ty = find_ty()
    if ty is None:
        print(
            "run_ty: `ty` is not installed. Install it in the project's dev "
            "environment (for example `pip install ty`).",
            file=sys.stderr,
        )
        return 2
    prefix = pick_python()
    if not (os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX")):
        print(
            f"run_ty: no virtualenv or conda env is active; checking against {prefix}. "
            "If that interpreter lacks the project's dependencies, ty reports "
            "unrelated errors: activate the project's environment and run again.",
            file=sys.stderr,
        )
    paths = search_paths(root)
    if not paths:
        print(
            "run_ty: no `src` directory with Python code found; running ty "
            f"without extra search paths (set {SEARCH_PATHS_ENV} to name them).",
            file=sys.stderr,
        )
    cmd = [*ty, "check", "--python", prefix]
    for sp in paths:
        cmd += ["--extra-search-path", str(sp)]
    return subprocess.call([*cmd, *argv], cwd=root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
