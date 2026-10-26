"""Turn the decision owner's briefing collection into SCENARIO.md: remove the line naming where it was produced and
relabel "FACT" as "Scenario". Nothing else changes (EPM-DEC-001-0102, item 4).

    uv run python -m pricing_demo.scenario <briefings.md>    # rewrite SCENARIO.md from the original
"""
import sys

from .config import ROOT

HEADER = """<!-- The demo's scenario: the decision owner's executive briefing collection for October 2026, kept as written except that
the line naming where it was produced is removed (the decision owner: "Remove any mention of ChatGPT", 2026-10-25) and
"FACT" reads "Scenario" (Claude's choice, delegated under EPM-DEC-001-0028; EPM-DEC-001-0102, item 4). Its figures calibrate the synthesized data only; they are never ontology facts. Where a figure differs
from published EIA data, EIA wins: README.md, "The scenario against EIA", lists each difference. -->
"""
PRODUCED_LINE = "> **Note:** This file consolidates"
LABELS = (("**FACT:**", "**Scenario:**"), ("**FACT —", "**Scenario —"), ("**FACT -", "**Scenario -"))


def transform(text):
    lines = [line for line in text.splitlines() if not line.startswith(PRODUCED_LINE)]
    out = []
    for line in lines:
        for old, new in LABELS:
            line = line.replace(old, new)
        out.append(line)
    body = "\n".join(out) + "\n"
    if "FACT" in body or "ChatGPT" in body:
        raise ValueError("a FACT label or the producing tool's name is left in the scenario")
    return HEADER + body


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        result = transform(f.read())
    with open(f"{ROOT}/SCENARIO.md", "w") as f:
        f.write(result)
