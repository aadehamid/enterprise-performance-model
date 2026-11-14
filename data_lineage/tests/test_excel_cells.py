import math
from pathlib import Path

import pandas as pd
import pytest

from excel_cells import clean_cell, pair_positional, readable_copy, split_multivalue


@pytest.mark.parametrize(
    ("raw", "clean"),
    [
        ("  udm_core.Sales_Fact  ", "udm_core.Sales_Fact"),
        ("udm\u200b_core.\ufeffSales\u200c_Fact\u200d", "udm_core.Sales_Fact"),
        ("Market\u00a0Sensing", "Market Sensing"),
        ("   ", None),
        ("", None),
        (None, None),
        (math.nan, None),
        (pd.NA, None),
        (math.inf, None),
        (-math.inf, None),
        (42, "42"),
    ],
)
def test_clean_cell(raw, clean):
    assert clean_cell(raw) == clean


@pytest.mark.parametrize(
    ("raw", "items"),
    [
        ("a.b\nc.d", ["a.b", "c.d"]),
        ("a.b, c.d", ["a.b", "c.d"]),
        ("a.b,\n c.d ,e.f", ["a.b", "c.d", "e.f"]),
        ("NA", []),
        ("a.b\nna\n", ["a.b"]),
        ("\u200ba.b", ["a.b"]),
        (None, []),
        (math.nan, []),
    ],
)
def test_split_multivalue(raw, items):
    assert split_multivalue(raw) == items


def test_pair_positional_matches_by_index():
    assert pair_positional(["mdm_core", "udm_core"], ["Locations_Dim", "Parameters_Fact"]) == [
        ("mdm_core", "Locations_Dim"),
        ("udm_core", "Parameters_Fact"),
    ]


def test_pair_positional_broadcasts_a_single_value():
    assert pair_positional(["udm_core"], ["A", "B"]) == [("udm_core", "A"), ("udm_core", "B")]
    assert pair_positional(["A", "B"], ["x"]) == [("A", "x"), ("B", "x")]


def test_pair_positional_warns_on_mismatch(caplog):
    assert pair_positional(["a", "b", "c"], ["x", "y"], "sheet row 7") == [("a", "x"), ("b", "y")]
    assert "sheet row 7" in caplog.text


def test_readable_copy_yields_a_copy_and_removes_it(tmp_path: Path):
    source = tmp_path / "book.xlsx"
    source.write_bytes(b"payload")
    with readable_copy(source) as copy:
        assert Path(copy) != source
        assert Path(copy).read_bytes() == b"payload"
    assert not Path(copy).exists()
    assert source.exists()
