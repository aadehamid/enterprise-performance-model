# apqc: the APQC element list

The full element list of APQC's Process Classification Framework for Downstream Petroleum, version 7.2.2, read from the vendored workbook (`../../reference/APQC-PCF-Downstream-Petroleum-v7.2.2.xlsx`, sheet "Combined"). `core` carries only the 251 elements its processes reference; with all 2,012, competency question 11 can list the elements with no local counterpart. Each element is described as `core` describes the ones it references, plus its name and hierarchy ID. APQC material is used under the APQC/IBM licence: `apqc-elements.ttl` carries the licence's notice and attribution in its header, as the licence requires of every copy; `core` states the PCF node's rights (`../../reference/README.md`). EPM-DEC-001-0060 records the choice.

| File | What |
|---|---|
| `build_apqc_elements.py`, `apqc-elements.ttl` | The build: 2,012 elements, 251 of them referenced by `core` 2.2.0 (2.1.0 until 2026-10-22, EPM-DEC-001-0076). `--verify` fails unless `apqc-elements.ttl` equals a fresh build. `scripts/check.sh` runs it |
| `test_apqc_elements.py` | Tests: the build is current, the count, every referenced element is listed, two pinned elements |

APQC is a consistency reference, not the process authority (tier 5, EPM-DEC-001-0059). An element without a counterpart is not a gap by itself: the scope decisions in `../apqc-scope-decisions.md` put whole areas out of scope.

The list is a reference file, in no release package: a package drops the Turtle comment that carries APQC's notice, which the licence requires on every copy (EPM-DEC-001-0078).
