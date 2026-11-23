#!/usr/bin/env python3
"""Guard the zerodep vendoring workflow against version downgrades.

The workflow calls this script in three steps:

* ``inspect`` reads ``zerodep status --json`` for each vendored tree, splits
  the modules into updatable and protected states, writes a plan, and
  publishes GitHub outputs plus a step summary.
* ``update`` applies the plan through an explicit module list and
  ``--no-deps``, so even a CLI that predates ``newer-than-upstream`` cannot
  downgrade a module through dependency resolution.
* ``verify`` re-reads the state and fails when a target stayed outdated or a
  locked version decreased.

Usage:

    zerodep_guard.py inspect PLAN SUMMARY OUTPUT_DIR...
    zerodep_guard.py update PLAN
    zerodep_guard.py verify PLAN SUMMARY
"""

import json
import subprocess
import sys
from pathlib import Path


def version_key(value):
    """Return a SemVer-compatible sort key, or None when unparseable."""
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text[:1] in ("v", "V"):
        text = text[1:]
    text = text.split("+", 1)[0]
    core, separator, prerelease = text.partition("-")
    try:
        parts = tuple(int(part) for part in core.split("."))
    except ValueError:
        return None
    if not parts:
        return None
    if len(parts) < 3:
        parts = parts + (0,) * (3 - len(parts))
    if not separator:
        return (parts, 1, ())
    identifiers = tuple(
        (0, int(part), "") if part.isdigit() else (1, 0, part)
        for part in prerelease.split(".")
    )
    return (parts, 0, identifiers)


def compare_versions(left, right):
    """Compare two versions, or return None when either is unparseable."""
    left_key = version_key(left)
    right_key = version_key(right)
    if left_key is None or right_key is None:
        return None
    return (left_key > right_key) - (left_key < right_key)


def run_status(directory):
    """Return the module rows from ``zerodep status --json`` in *directory*."""
    result = subprocess.run(
        ["zerodep", "status", "--json"],
        cwd=directory,
        text=True,
        capture_output=True,
    )
    if result.stderr.strip():
        print(result.stderr.rstrip(), file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(
            "zerodep status failed in {} (rc={})".format(directory, result.returncode)
        )
    return json.loads(result.stdout)["modules"]


def classify(rows):
    """Split rows into updatable and protected groups."""
    groups = {
        "updatable": [],
        "same_version": [],
        "newer": [],
        "unknown": [],
        "manual": [],
    }
    for row in rows:
        state = row.get("state")
        if state == "up-to-date":
            continue
        if state == "missing":
            groups["updatable"].append(row)
            continue
        if state == "newer-than-upstream":
            groups["newer"].append(row)
            continue
        if state == "version-uncomparable":
            groups["unknown"].append(row)
            continue
        if state == "outdated":
            compared = compare_versions(
                row.get("installed_version"), row.get("latest_version")
            )
            if compared is None:
                groups["unknown"].append(row)
            elif compared > 0:
                groups["newer"].append(row)
            else:
                groups["updatable"].append(row)
                if compared == 0:
                    groups["same_version"].append(row)
            continue
        groups["manual"].append(row)
    return groups


def describe(row):
    """Return a PR-body line for an updatable row."""
    locked = row.get("installed_version") or "\u2014"
    latest = row.get("latest_version") or "\u2014"
    if row.get("state") == "missing":
        return "- {}: missing -> {} (reinstall)".format(row["name"], latest)
    if compare_versions(row.get("installed_version"), row.get("latest_version")) == 0:
        return (
            "- {}: content differs at version {} "
            "(hash changed, version unchanged)"
        ).format(row["name"], latest)
    return "- {}: {} -> {} (`{}`)".format(
        row["name"], locked, latest, row.get("state")
    )


def inspect(plan_path, summary_path, directories):
    """Classify every directory, write the plan, and publish outputs."""
    plan = {
        "dirs": {},
        "newer": [],
        "unknown": [],
        "manual": [],
        "updatable": [],
    }
    lines = ["### zerodep update check", ""]
    has_updates = False
    found_any = False

    for directory in directories:
        rows = run_status(directory)
        groups = classify(rows)
        if any(groups.values()):
            found_any = True
        names = [row["name"] for row in groups["updatable"]]
        plan["dirs"][directory] = {"before": rows, "updatable": names}
        for key in ("newer", "unknown", "manual", "updatable"):
            for row in groups[key]:
                plan[key].append(dict(row, dir=directory))

        if len(directories) > 1:
            lines.append("#### `{}`".format(directory))
            lines.append("")

        if groups["updatable"]:
            has_updates = True
            lines.append("**Updatable**")
            lines.extend(describe(row) for row in groups["updatable"])
            lines.append("")
        if groups["newer"]:
            lines.append("**Skipped: locked version is newer than upstream**")
            for row in groups["newer"]:
                lines.append(
                    "- {}: locked {} > upstream {} \u2014 not downgraded. Keep the "
                    "current source with `zerodep --ref <commit> update`, or "
                    "accept the older release with "
                    "`zerodep update {} --force`.".format(
                        row["name"],
                        row.get("installed_version") or "\u2014",
                        row.get("latest_version") or "\u2014",
                        row["name"],
                    )
                )
            lines.append("")
        if groups["unknown"]:
            lines.append("**Skipped: versions cannot be compared**")
            for row in groups["unknown"]:
                lines.append(
                    "- {}: locked {} vs upstream {} \u2014 not replaced "
                    "automatically".format(
                        row["name"],
                        row.get("installed_version") or "\u2014",
                        row.get("latest_version") or "\u2014",
                    )
                )
            lines.append("")
        if groups["manual"]:
            lines.append("**Needs a human decision**")
            for row in groups["manual"]:
                lines.append("- {}: `{}`".format(row["name"], row.get("state")))
            lines.append("")

    if not found_any:
        lines.append("All installed modules are up to date.")
        lines.append("")

    for row in plan["newer"]:
        print(
            "::warning::{}: locked {} is newer than upstream {}; not "
            "downgraded".format(
                row["name"],
                row.get("installed_version") or "\u2014",
                row.get("latest_version") or "\u2014",
            ),
            file=sys.stderr,
        )
    for row in plan["unknown"]:
        print(
            "::warning::{}: cannot compare locked {} with upstream {}; "
            "skipped".format(
                row["name"],
                row.get("installed_version") or "\u2014",
                row.get("latest_version") or "\u2014",
            ),
            file=sys.stderr,
        )

    Path(plan_path).write_text(json.dumps(plan), encoding="utf-8")
    with open(summary_path, "a", encoding="utf-8") as summary:
        summary.write("\n".join(lines) + "\n")

    print("has_updates={}".format("true" if has_updates else "false"))
    print("modules<<EOF")
    print("\n".join(lines))
    print("EOF")


def update(plan_path):
    """Apply the plan one directory at a time, with an explicit module list."""
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    for directory, entry in plan["dirs"].items():
        names = entry["updatable"]
        if not names:
            continue
        command = ["zerodep", "update", "--no-deps"] + names
        print("== {}: {}".format(directory, " ".join(command)), flush=True)
        result = subprocess.run(command, cwd=directory)
        if result.returncode != 0:
            raise SystemExit(
                "zerodep update failed in {} (rc={})".format(
                    directory, result.returncode
                )
            )


def verify(plan_path, summary_path):
    """Fail when a target stayed outdated or a locked version decreased."""
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    problems = []
    checked = 0
    for directory, entry in plan["dirs"].items():
        if not entry["updatable"]:
            continue
        after = {row["name"]: row for row in run_status(directory)}
        restored = {
            row["name"] for row in entry["before"] if row.get("state") == "missing"
        }
        for name in entry["updatable"]:
            row = after.get(name)
            state = row.get("state") if row else "absent"
            if state != "up-to-date":
                problems.append("{}: {} is {}".format(directory, name, state))
            checked += 1
        for row in entry["before"]:
            if row["name"] in restored:
                continue
            new = after.get(row["name"])
            if new is None:
                continue
            old_key = version_key(row.get("installed_version"))
            new_key = version_key(new.get("installed_version"))
            if old_key is not None and new_key is not None and new_key < old_key:
                problems.append(
                    "{}: {} went from {} to {}".format(
                        directory,
                        row["name"],
                        row.get("installed_version"),
                        new.get("installed_version"),
                    )
                )
    if problems:
        raise SystemExit("zerodep guard failed:\n  " + "\n  ".join(problems))
    with open(summary_path, "a", encoding="utf-8") as summary:
        summary.write(
            "\nUpdate verified: {} module(s) up to date; no locked version "
            "decreased.\n".format(checked)
        )


def main(argv):
    """Dispatch a subcommand."""
    if len(argv) < 2:
        raise SystemExit(__doc__)
    command = argv[1]
    if command == "inspect" and len(argv) >= 5:
        inspect(argv[2], argv[3], argv[4:])
    elif command == "update" and len(argv) == 3:
        update(argv[2])
    elif command == "verify" and len(argv) == 4:
        verify(argv[2], argv[3])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
