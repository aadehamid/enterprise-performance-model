#!/usr/bin/env python3
"""Fixture tests for the PTC bind in step3c-workbook-validate.py.

Covers the Step 3d close path: a retired row may keep citing a Closed PTC;
a blocked row may not.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

SCRIPT = Path(__file__).resolve().parent / "step3c-workbook-validate.py"

HEADERS = [
    "slug",
    "name",
    "definition",
    "scope_note",
    "in_scope",
    "out_of_scope",
    "alt_labels",
    "status",
    "concept_type_check",
    "primary_purpose",
    "reference_sources",
    "open_questions",
    "process_horizon",
    "terminology_notes",
]


def _workbook(rows: list[dict]) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "Review & authoring"
    ws.append(HEADERS)
    for row in rows:
        ws.append([row.get(h, "") for h in HEADERS])
    path = Path(tempfile.mkdtemp()) / "wb.xlsx"
    wb.save(path)
    return path


def _register(status: str, tmp: Path) -> Path:
    path = tmp / "ptc.md"
    path.write_text(
        f"## PTC-001 — test\n\n**Status:** {status}\n",
        encoding="utf-8",
    )
    return path


def _idmap(tmp: Path) -> Path:
    path = tmp / "idmap.json"
    path.write_text("[]", encoding="utf-8")
    return path


def _run(workbook: Path, register: Path, idmap: Path) -> tuple[int, str, str]:
    out = Path(tempfile.mkdtemp()) / "findings.md"
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--workbook",
            str(workbook),
            "--ptc-register",
            str(register),
            "--identity-map",
            str(idmap),
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    report = out.read_text(encoding="utf-8") if out.exists() else ""
    return proc.returncode, proc.stdout + proc.stderr, report


def _parked(slug: str, status: str) -> dict:
    return {
        "slug": slug,
        "name": slug,
        "status": status,
        "terminology_notes": "Parked on PTC-001.",
    }


def _pending() -> dict:
    return {"slug": "KEEP-QUEUE", "name": "Keep queue", "status": "pending"}


class PtcClosedRetiredPath(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.idmap = _idmap(self.tmp)

    def test_retired_citation_survives_closed_ptc(self) -> None:
        wb = _workbook([_parked("CM-RETIRED", "retired"), _pending()])
        register = _register("**Closed** 2026-09-19", self.tmp)
        code, log, report = _run(wb, register, self.idmap)
        self.assertNotIn("[ptc-closed]", report, report)
        self.assertEqual(code, 0, log)

    def test_blocked_citation_fails_closed_ptc(self) -> None:
        wb = _workbook([_parked("CM-BLOCKED", "blocked"), _pending()])
        register = _register("**Closed** 2026-09-19", self.tmp)
        code, log, report = _run(wb, register, self.idmap)
        self.assertIn("[ptc-closed]", report, report)
        self.assertEqual(code, 1, log)

    def test_retired_citation_ok_while_ptc_open(self) -> None:
        wb = _workbook([_parked("CM-RETIRED", "retired"), _pending()])
        register = _register("Open — awaiting tree pass", self.tmp)
        code, log, report = _run(wb, register, self.idmap)
        self.assertNotIn("[ptc-closed]", report, report)
        self.assertEqual(code, 0, log)


if __name__ == "__main__":
    unittest.main()
