"""Tests for ci/templates/scripts/zerodep_guard.py (no zerodep CLI is run)."""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "zerodep_guard.py"

_spec = importlib.util.spec_from_file_location("zerodep_guard", SCRIPT)
assert _spec is not None and _spec.loader is not None
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)


def _row(name, state, locked=None, latest=None, **extra):
    row = {
        "name": name,
        "state": state,
        "installed_version": locked,
        "latest_version": latest,
    }
    row.update(extra)
    return row


def _plan(before, updatable):
    return {"dirs": {".": {"before": before, "updatable": updatable}}}


def _plan_file(tmp_path, before, updatable):
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(_plan(before, updatable)), encoding="utf-8")
    return str(path)


def _summary(tmp_path):
    path = tmp_path / "summary.md"
    path.write_text("", encoding="utf-8")
    return path


def test_classify_protects_locked_newer():
    groups = guard.classify([_row("a", "outdated", "0.3.1", "0.3.0")])
    assert [row["name"] for row in groups["newer"]] == ["a"]
    assert groups["updatable"] == []


def test_classify_routes_unparseable_to_unknown():
    groups = guard.classify([_row("a", "outdated", "dev", "1.0.0")])
    assert [row["name"] for row in groups["unknown"]] == ["a"]


def test_classify_missing_is_updatable():
    groups = guard.classify([_row("a", "missing", "9.9.9", "0.3.0")])
    assert [row["name"] for row in groups["updatable"]] == ["a"]


def test_classify_missing_deps_is_manual():
    row = _row("a", "up-to-date", "1.0.0", "1.0.0", missing_deps=["b"])
    groups = guard.classify([row])
    assert [item["name"] for item in groups["manual"]] == ["a"]
    assert groups["updatable"] == []


def test_expected_local_moves_patched_module(monkeypatch):
    monkeypatch.setattr(guard, "EXPECTED_LOCAL", {"a"})
    groups = guard.classify([_row("a", "locally-modified", "1.0.0", "1.0.0")])
    assert [row["name"] for row in groups["expected"]] == ["a"]
    assert groups["manual"] == []


@pytest.mark.parametrize(
    "left,right",
    [
        ("0.10.0", "0.9.0"),
        ("v1.2.3", "1.2.2"),
        ("0.3.1-rc.10", "0.3.1-rc.2"),
        ("1.0", "0.9.9"),
    ],
)
def test_version_key_orders(left, right):
    assert guard.compare_versions(left, right) == 1


def test_version_key_pads_missing_components():
    assert guard.compare_versions("1.0", "1.0.0") == 0


def test_verify_fails_on_downgrade(tmp_path, monkeypatch):
    plan = _plan_file(tmp_path, [_row("a", "outdated", "0.5.1", "0.4.3")], ["a"])
    monkeypatch.setattr(
        guard,
        "run_status",
        lambda directory: [_row("a", "up-to-date", "0.4.3", "0.4.3")],
    )
    with pytest.raises(SystemExit, match="went from 0.5.1 to 0.4.3"):
        guard.verify(plan, str(_summary(tmp_path)))


def test_verify_fails_on_missing_deps(tmp_path, monkeypatch):
    plan = _plan_file(tmp_path, [_row("a", "outdated", "1.0.0", "1.1.0")], ["a"])
    monkeypatch.setattr(
        guard,
        "run_status",
        lambda directory: [
            _row("a", "up-to-date", "1.1.0", "1.1.0", missing_deps=["b"])
        ],
    )
    with pytest.raises(SystemExit, match="is missing b"):
        guard.verify(plan, str(_summary(tmp_path)))


def test_verify_reports_restored_older_missing(tmp_path, monkeypatch):
    plan = _plan_file(tmp_path, [_row("a", "missing", "9.9.9", "0.3.0")], ["a"])
    monkeypatch.setattr(
        guard,
        "run_status",
        lambda directory: [_row("a", "up-to-date", "0.3.0", "0.3.0")],
    )
    summary = _summary(tmp_path)
    guard.verify(plan, str(summary))
    text = summary.read_text(encoding="utf-8")
    assert "no unexpected locked version decreased" in text
    assert "reinstalled at 0.3.0 (lock had 9.9.9)" in text


def test_require_vendor_config_rejects_missing_section(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'x'\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match=r"no \[tool.zerodep\] vendor-dir"):
        guard.require_vendor_config(str(tmp_path))


def test_require_vendor_config_accepts_section(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        "[tool.zerodep]\nvendor-dir = '_vendor'\n", encoding="utf-8"
    )
    guard.require_vendor_config(str(tmp_path))


def test_parse_status_accepts_expected_shape():
    payload = json.dumps(
        {"lock": True, "modules": [_row("a", "up-to-date", "1.0.0", "1.0.0")]}
    )
    rows = guard.parse_status(".", payload)
    assert rows[0]["name"] == "a"


def test_parse_status_warns_without_lock(capsys):
    payload = json.dumps({"lock": False, "modules": [_row("a", "up-to-date")]})
    rows = guard.parse_status(".", payload)
    assert rows[0]["name"] == "a"
    assert "no lock file" in capsys.readouterr().err


def test_parse_status_rejects_empty_modules():
    with pytest.raises(SystemExit, match="found no modules"):
        guard.parse_status(".", json.dumps({"lock": True, "modules": []}))


def test_parse_status_rejects_renamed_top_level_key():
    with pytest.raises(SystemExit, match="modules"):
        guard.parse_status(".", json.dumps({"module": []}))


def test_parse_status_rejects_missing_row_key():
    row = {"name": "a", "state": "up-to-date", "installed_version": "1.0.0"}
    with pytest.raises(SystemExit, match="latest_version"):
        guard.parse_status(".", json.dumps({"lock": True, "modules": [row]}))


def test_parse_status_rejects_non_json():
    with pytest.raises(SystemExit, match="Expecting value"):
        guard.parse_status(".", "not json")


def test_emit_warnings_annotates_every_group(capsys):
    rows = [
        _row("a", "outdated", "0.3.1", "0.3.0"),
        _row("b", "version-uncomparable", "dev", "1.0.0"),
        _row("c", "conflict", "1.0.0", "1.0.0"),
    ]
    groups = guard.classify(rows)
    guard.emit_warnings(groups["newer"], groups["unknown"], groups["manual"])
    err = capsys.readouterr().err
    assert "a: locked 0.3.1 is newer than upstream 0.3.0" in err
    assert "b: cannot compare locked dev with upstream 1.0.0" in err
    assert "c: conflict; needs a human decision" in err
