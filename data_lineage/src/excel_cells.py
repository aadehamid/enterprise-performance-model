"""Cleaning rules for values read out of Excel source artifacts (AGENTS.md data cleaning conventions)."""

import logging
import math
import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager

import pandas as pd

log = logging.getLogger(__name__)

_INVISIBLE = str.maketrans({"\u200b": None, "\u200c": None, "\u200d": None, "\ufeff": None, "\u00a0": " "})


def clean_cell(value) -> str | None:
    """Text of a cell with invisible Unicode removed, NBSP as a space, trimmed; None for blank, NaN or infinity."""
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return None
    if isinstance(value, float) and math.isinf(value):
        return None
    return str(value).translate(_INVISIBLE).strip() or None


def split_multivalue(value) -> list[str]:
    """Items of a multi-value cell split on newlines and commas, without blanks or "NA"."""
    text = clean_cell(value)
    if text is None:
        return []
    items = (part.strip() for line in text.split("\n") for part in line.split(","))
    return [item for item in items if item and item.upper() != "NA"]


def pair_positional(left: list[str], right: list[str], context: str = "") -> list[tuple[str, str]]:
    """Pair two multi-value cells index by index; a single value pairs with every value opposite it."""
    if len(left) == 1:
        return [(left[0], r) for r in right]
    if len(right) == 1:
        return [(l, right[0]) for l in left]
    if len(left) != len(right):
        log.warning("Multi-value count mismatch %s: %d vs %d (%r / %r)", context, len(left), len(right), left, right)
    return list(zip(left, right))


@contextmanager
def readable_copy(path):
    """Yield a temporary copy of `path`, falling back to PowerShell Copy-Item when Excel holds an exclusive lock."""
    tmp_dir = tempfile.mkdtemp()
    copy = os.path.join(tmp_dir, os.path.basename(path))
    try:
        try:
            shutil.copy2(path, copy)
        except PermissionError:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", f"Copy-Item -LiteralPath '{path}' -Destination '{copy}' -Force"],
                check=True,
            )
        yield copy
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
