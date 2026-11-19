"""Tests for scripts/dev/run_ty.py (ty itself is not run)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "run_ty", Path(__file__).parent.parent / "scripts" / "dev" / "run_ty.py"
)
assert _SPEC is not None and _SPEC.loader is not None
rt = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(rt)


def _package(src: Path, name: str) -> None:
    (src / name).mkdir(parents=True)
    (src / name / "__init__.py").write_text("")


@pytest.fixture
def fake_repo(tmp_path):
    """A monorepo with two ``src`` roots plus decoys that must be ignored."""
    (tmp_path / ".git").mkdir()
    _package(tmp_path / "packages" / "core" / "src", "core")
    _package(tmp_path / "packages" / "gateway" / "src", "gateway")
    (tmp_path / "docs" / "src").mkdir(parents=True)  # no Python: ignored
    (tmp_path / "docs" / "src" / "index.md").write_text("")
    _package(tmp_path / ".venv" / "src", "hidden")  # hidden dir: ignored
    _package(tmp_path / "node_modules" / "x" / "src", "x")  # skipped dir
    _package(tmp_path / "a" / "b" / "c" / "d" / "src", "deep")  # too deep
    sub = tmp_path / "tests" / "deep"
    sub.mkdir(parents=True)
    return tmp_path, sub


def test_find_repo_root_prefers_git(fake_repo, tmp_path):
    root, sub = fake_repo
    (root / "packages" / "core" / "pyproject.toml").write_text("")
    assert rt.find_repo_root(root / "packages" / "core" / "src") == root
    assert rt.find_repo_root(sub) == root


def test_find_repo_root_accepts_worktree_git_file(tmp_path):
    (tmp_path / ".git").write_text("gitdir: /elsewhere\n")
    assert rt.find_repo_root(tmp_path) == tmp_path


def test_find_repo_root_falls_back_to_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text("")
    sub = tmp_path / "x"
    sub.mkdir()
    assert rt.find_repo_root(sub) == tmp_path


def test_discover_finds_only_real_source_roots(fake_repo):
    root, _ = fake_repo
    found = [p.relative_to(root).as_posix() for p in rt.discover_search_paths(root)]
    assert found == ["packages/core/src", "packages/gateway/src"]


def test_discover_accepts_top_level_module(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.py").write_text("")
    assert rt.discover_search_paths(tmp_path) == [tmp_path / "src"]


def test_discover_orders_shallowest_first(tmp_path):
    _package(tmp_path / "pkgs" / "z" / "src", "z")
    _package(tmp_path / "src", "top")
    found = [
        p.relative_to(tmp_path).as_posix() for p in rt.discover_search_paths(tmp_path)
    ]
    assert found == ["src", "pkgs/z/src"]


def test_override_replaces_discovery(fake_repo, monkeypatch):
    root, _ = fake_repo
    monkeypatch.setenv(rt.SEARCH_PATHS_ENV, f"lib{rt.os.pathsep}other/src")
    assert rt.search_paths(root) == [root / "lib", root / "other" / "src"]


def test_pick_python_precedence(monkeypatch):
    monkeypatch.setenv("VIRTUAL_ENV", "/v")
    monkeypatch.setenv("CONDA_PREFIX", "/c")
    assert rt.pick_python() == "/v"
    monkeypatch.delenv("VIRTUAL_ENV")
    assert rt.pick_python() == "/c"
    monkeypatch.delenv("CONDA_PREFIX")
    assert rt.pick_python() == rt.sys.prefix


def test_command_puts_checkout_sources_first(fake_repo, monkeypatch):
    root, sub = fake_repo
    seen = {}

    def fake_call(cmd, cwd):
        seen["cmd"], seen["cwd"] = cmd, cwd
        return 7

    monkeypatch.chdir(sub)
    monkeypatch.delenv(rt.SEARCH_PATHS_ENV, raising=False)
    monkeypatch.setenv("VIRTUAL_ENV", "/v")
    monkeypatch.setattr(rt, "find_ty", lambda: ["ty"])
    monkeypatch.setattr(rt.subprocess, "call", fake_call)
    assert rt.main(["--output-format", "concise"]) == 7
    cmd = seen["cmd"]
    assert cmd[:4] == ["ty", "check", "--python", "/v"]
    for rel in ("packages/core/src", "packages/gateway/src"):
        i = cmd.index(str(root / rel))
        assert cmd[i - 1] == "--extra-search-path"
    assert cmd[-2:] == ["--output-format", "concise"]
    assert seen["cwd"] == root


def test_no_source_dirs_still_runs_ty(tmp_path, monkeypatch, capsys):
    (tmp_path / ".git").mkdir()
    seen = {}
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(rt.SEARCH_PATHS_ENV, raising=False)
    monkeypatch.setenv("VIRTUAL_ENV", "/v")
    monkeypatch.setattr(rt, "find_ty", lambda: ["ty"])
    monkeypatch.setattr(
        rt.subprocess, "call", lambda cmd, cwd=None: seen.setdefault("cmd", cmd) and 0
    )
    assert rt.main([]) == 0
    assert "--extra-search-path" not in seen["cmd"]
    assert "no `src` directory" in capsys.readouterr().err


def test_outside_a_checkout_is_an_error(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(rt, "find_repo_root", lambda start: None)
    assert rt.main([]) == 2
    assert "inside a git checkout" in capsys.readouterr().err


def test_missing_ty_is_an_error(fake_repo, monkeypatch, capsys):
    _, sub = fake_repo
    monkeypatch.chdir(sub)
    monkeypatch.setattr(rt, "find_ty", lambda: None)
    assert rt.main([]) == 2
    assert "not installed" in capsys.readouterr().err


def test_main_warns_when_no_environment_is_active(monkeypatch, capsys, tmp_path):
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    monkeypatch.delenv("CONDA_PREFIX", raising=False)
    monkeypatch.delenv(rt.SEARCH_PATHS_ENV, raising=False)
    monkeypatch.setattr(rt, "find_repo_root", lambda start: tmp_path)
    monkeypatch.setattr(rt, "find_ty", lambda: ["ty"])
    monkeypatch.setattr(rt.subprocess, "call", lambda cmd, cwd=None: 0)
    assert rt.main([]) == 0
    assert "no virtualenv or conda env is active" in capsys.readouterr().err
