#!/usr/bin/env python3
"""Blast-radius gate for the Step 4 evidence package (2026-09-25 verification).

Fails loud (nonzero exit) on the first inconsistency. Proves:
  1. Every generated evidence CSV cites the pinned baseline SHA on every row.
  2. Mention arithmetic reconciles from the actual files: 1066+237+12+1+2=1318.
  3. canonical-facts.csv has exactly 866 distinct facts; contradictions.csv has 0 (no-two-cycle rule).
  4. No orphan row_ids across the package.
  5. Sample review has 51 verdicts, all OK or FLAG.
  6. Label report: 104 rows, 90 carried-approved, 14 undecided with blank decisions.
"""
import csv, re, sys

SHA = open("PINNED_SHA.txt").read().strip()
fails = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond: fails.append(name)

def rows(fn):
    with open(fn) as f: return list(csv.DictReader(f))

# 1. SHA pin on every generated CSV
sha_files = ["target-report/target-dispositions-v2.csv", "target-report/context-pass.csv",
             "target-report/sibling-review-package-v2.csv",
             "label-report/label-dispositions-v1.2.csv",
             "requires-review.csv", "assures-review.csv", "enables-review.csv"]
for fn in sha_files:
    rs = rows(fn)
    bad = [r.get("row_id", r.get("concept_slug")) for r in rs if r.get("baseline_sha") != SHA]
    check(f"sha-pin {fn}", not bad, f"{len(bad)} rows with wrong/missing sha")

# 2. mention arithmetic from the files
v2 = rows("target-report/target-dispositions-v2.csv")
ctx = {r["row_id"]: r["outcome"] for r in rows("target-report/context-pass.csv")}
# property-rule holds (Hamid 2026-09-24; enabledBy verdicts same day):
# REL-00503 held (mutual informedBy, this direction B-only).
# REL-01312 and REL-01053 held for source-workbook correction (reverse
# enablement means control/constraint or close-feed consumption, not capability
# enablement). REL-01303 and REL-01056 approved for emission — no longer held.
# 2026-09-25: REL-00758, REL-01094, REL-01131, REL-01192 held for source
# correction ("enables" flattening "informs"); REL-00936 held for source
# classification review.
# 2026-09-25: REL-00445 held for source correction ("enables" flattening
# "informed-by"; PTC-002: planning decides, trading advises).
# 2026-09-25: REL-00208 held for workbook correction (rejected remap to
# dependsOnOutputOf; emit no triple).
# 2026-09-26: 28 G1b rows held under G1bNoVerbChange (enables with only
# reverse informed-by evidence; stored core:dependsOnOutputOf facts removed,
# Rule 11). REL-01224 is context-held and needs no property hold.
prop_holds = {"REL-00503", "REL-01312", "REL-01053",
              "REL-00758", "REL-01094", "REL-01131", "REL-01192", "REL-00936",
              "REL-00445", "REL-00208",
              "REL-01106", "REL-00917", "REL-00884", "REL-01065",
              "REL-00002", "REL-00013", "REL-00466", "REL-00469", "REL-00764",
              "REL-00768", "REL-00773", "REL-00912", "REL-00923", "REL-00925",
              "REL-00152", "REL-00262", "REL-00458", "REL-01122", "REL-01129",
              "REL-00263", "REL-00436", "REL-00440", "REL-00455", "REL-00712",
              "REL-00750", "REL-01064", "REL-01206",
              "REL-00140", "REL-00499", "REL-00565", "REL-00648", "REL-00679",
              "REL-00709", "REL-00732", "REL-00973", "REL-00974", "REL-00977",
              "REL-01108", "REL-01112", "REL-01148", "REL-01151", "REL-01154",
              "REL-01181", "REL-01184", "REL-01191", "REL-01194", "REL-01197",
              "REL-01213", "REL-01225", "REL-01230", "REL-01233", "REL-01234",
              "REL-01273", "REL-01296", "REL-01315"}
promoted = sum(1 for r in v2 if r["disposition"] == "ResolvedToConcept") + \
           sum(1 for v in ctx.values() if v == "PROMOTE") - len(prop_holds)
held_ctx = sum(1 for v in ctx.values() if v == "HOLD") + len(prop_holds)
ambig = sum(1 for r in v2 if r["disposition"] == "AmbiguousDeferred")
ext = sum(1 for r in v2 if r["disposition"] == "ExternalGovernanceReference")
flow = sum(1 for r in v2 if r["disposition"] == "StructuredFlowValue")
check("mention-arithmetic", promoted + held_ctx + ambig + ext + flow == 1318 == len(v2),
      f"{promoted}+{held_ctx}+{ambig}+{ext}+{flow}={promoted+held_ctx+ambig+ext+flow} vs {len(v2)}")
check("promoted==1066", promoted == 1066, str(promoted))
check("held==237", held_ctx == 237, str(held_ctx))

# 2b. enabledBy control cases (Hamid verdicts 2026-09-24/25), checked against the
# STORED canonical fact — not the verb string. "Approved as core:enables"
# means the stored triple is (target_slug, core:enabledBy, source_slug), with
# core:enables available as its inverse. Row-level verdicts override the
# G1/G2/G3 group proposal for these rows (see EN_ENABLEDBY_OVERRIDE in
# mapping_v2.py). If future logic stores a different predicate — or drops the
# triple — for any of these rows, the gate must fail.
v2d = {r["row_id"]: r for r in v2}
cfacts = rows("canonical-facts.csv")
_fact_rowids = {}
for fr in cfacts:
    _fact_rowids.setdefault((fr["subject"], fr["predicate"], fr["object"]), [])
    _fact_rowids[(fr["subject"], fr["predicate"], fr["object"])].extend(fr["row_ids"].split(";"))
def _tgt(rid):
    r = v2d[rid]
    cands = r["candidate_slugs"].split(" | ") if r["candidate_slugs"] else []
    assert len(cands) == 1, rid
    return cands[0]
def _stored(rid):
    """Expected stored (subject, predicate, object) per the canonical direction
    table (see stored_fact in mapping_v2.py). Inverse-pair verbs are stored
    from the dependent side."""
    s = v2d[rid]["source_slug"]; t = _tgt(rid); v = v2d[rid]["verb"]
    if v == "enables": return (t, "core:enabledBy", s)
    if v == "follows": return (t, "core:precedes", s)
    if v == "informs": return (t, "core:informedBy", s)
    if v == "constrains": return (t, "core:constrainedBy", s)
    if v == "triggers": return (t, "core:triggeredBy", s)
    if v == "assures": return (t, "core:assuredBy", s)
    if v == "governed-by": return (s, "core:governedBy", t)
    if v == "uses-input": return (s, "core:dependsOnOutputOf", t)
    if v == "informed-by": return (s, "core:informedBy", t)
    if v == "precedes": return (s, "core:precedes", t)
    if v == "requires": return (s, "core:requires", t)
    if v == "constrained-by": return (s, "core:constrainedBy", t)
    raise ValueError(v)
for rid in ("REL-01303", "REL-01056"):
    fact = _stored(rid)
    check(f"control-case stored {rid} as {fact[1]}",
          fact in _fact_rowids and rid in _fact_rowids[fact],
          f"approved as core:enables per Hamid 2026-09-24/25; expected stored fact {fact}")
# 2026-09-26 (G3-B5): REL-00129, REL-00243, REL-00304, REL-00728, REL-01006,
# REL-01016 were removed from the override set — prior approvals superseded
# under the nearness-only identity rule. Their facts were verified unique
# and removed; they are now no-fact hold controls (see the control-case
# hold list below).
def _emits_nothing(rid):
    return all(rid not in rids for rids in _fact_rowids.values())
for rid in ("REL-01312", "REL-01053", "REL-00758", "REL-01094", "REL-01131",
            "REL-01192", "REL-00936", "REL-00445", "REL-00208", "REL-01106",
            "REL-00917", "REL-00884", "REL-01065",
            "REL-00002", "REL-00013", "REL-00466", "REL-00469", "REL-00764",
            "REL-00768", "REL-00773", "REL-00912", "REL-00923", "REL-00925",
            "REL-00262", "REL-00458", "REL-01122", "REL-01129",
            "REL-00263", "REL-00440", "REL-00455", "REL-00712",
            "REL-00750", "REL-01064", "REL-01206",
            "REL-00129", "REL-00243", "REL-00304", "REL-00489",
            "REL-00728", "REL-01006", "REL-01016", "REL-01124",
            "REL-01174"):
    check(f"control-case hold {rid}", _emits_nothing(rid),
          "must stay held (source correction) per Hamid 2026-09-24/25: no stored triple")
# Hamid 2026-09-26: G3-B1 verdicts (D:hamid-verdict). Target identity
# unconfirmed for nearness-only candidates — no stored triple. These two
# rows were previously listed in the approved-emission control-case list
# on a mistaken basis (they were never row-level approved); observed
# failing 2026-09-26 after B1 verdicts, corrected here.
for rid in ("REL-00059", "REL-00133"):
    check(f"control-case hold {rid}", _emits_nothing(rid),
          "must stay held (G3-B1 target identity unconfirmed) per Hamid 2026-09-26: no stored triple")
# REL-00428: genuine 2026-09-25 row-level approval (review32-enables-batch,
# "validated feedstock-quality data underpins term-slate quality screening")
# SUPERSEDED by Hamid's 2026-09-26 G3-B2 verdict (D:hamid-verdict /
# TargetIdentityUnconfirmed): the approval rested on semantic plausibility,
# but the nearness-only identity rule requires source-backed target identity
# before any predicate verdict; the later row-level verdict is
# authoritative. Removed from EN_ENABLEDBY_OVERRIDE 2026-09-26.
check("control-case hold REL-00428", _emits_nothing("REL-00428"),
      "must stay held (G3-B2 supersession of 2026-09-25 approval): no stored triple")
# REL-00770: genuine 2026-09-25 row-level approval (review32-enables-batch:
# "Account planning explicitly feeds Sales Execution with account-level
# objectives, opportunity maps, actions, evidence") SUPERSEDED by Hamid's
# 2026-09-26 G3-B3 verdict (D:hamid-verdict / TargetIdentityUnconfirmed /
# Supersedes2026-09-25Approval). Predicate plausibility cannot substitute
# for source-backed target identity under the Hamid-approved nearness-only
# identity rule. Prior decision retained in provenance as superseded, not
# deleted. Removed from EN_ENABLEDBY_OVERRIDE 2026-09-26.
check("control-case hold REL-00770", _emits_nothing("REL-00770"),
      "must stay held (G3-B3 supersession of 2026-09-25 approval): no stored triple")
# REL-00939: genuine 2026-09-25 row-level approval (review32-enables-batch:
# "approved financing/payment methods, terms, eligibility, commercial
# rules are governed prerequisites for billing") SUPERSEDED by Hamid's
# 2026-09-26 G3-B4 verdict (D:hamid-verdict / TargetIdentityUnconfirmed /
# Supersedes2026-09-25Approval). The source row never names Manage Customer
# Invoicing and Billing as its target; under the nearness-only identity
# rule, a plausible relationship cannot stand in for a named target. Prior
# decision retained in provenance as superseded. Removed from
# EN_ENABLEDBY_OVERRIDE 2026-09-26.
check("control-case hold REL-00939", _emits_nothing("REL-00939"),
      "must stay held (G3-B4 supersession of 2026-09-25 approval): no stored triple")
# 2d. governed-by control cases (Hamid verdicts 2026-09-25), checked against
# the stored fact (source, core:governedBy, target) — never on structural
# nearness. The 3 held rows must contribute to no stored triple.
for rid in ("REL-00050", "REL-00067", "REL-00190", "REL-00394", "REL-00399",
            "REL-00406", "REL-00858", "REL-00907", "REL-00937", "REL-01005",
            "REL-01228", "REL-01256", "REL-01313"):
    fact = _stored(rid)
    check(f"control-case stored {rid} as {fact[1]}",
          fact in _fact_rowids and rid in _fact_rowids[fact],
          f"approved as core:governedBy per Hamid 2026-09-25; expected stored fact {fact}")
for rid in ("REL-00274", "REL-01143", "REL-01286"):
    check(f"control-case hold {rid}", _emits_nothing(rid),
          "must stay held per Hamid 2026-09-25: no stored triple")
# 2f. requires control cases (Hamid verdicts 2026-09-25, as amended 2026-09-26).
# The 4 still-approved rows must store (source, core:requires, target).
# REL-00208 is asserted above via _emits_nothing: neither requires nor
# dependsOnOutputOf may be stored. REL-00873 was superseded 2026-09-26
# (identity-rule scope ruling: no rule 5 route) — it must emit nothing and
# its former core:requires fact must be absent.
for rid in ("REL-00158", "REL-00168", "REL-00247", "REL-00872"):
    fact = _stored(rid)
    check(f"control-case stored {rid} as {fact[1]}",
          fact in _fact_rowids and rid in _fact_rowids[fact],
          f"approved as core:requires per Hamid 2026-09-25; expected stored fact {fact}")
check("control-case hold REL-00873", _emits_nothing("REL-00873"),
      "superseded 2026-09-26: no stored triple; fact removed")
# 2g. assures control cases (Hamid verdicts 2026-09-26). The 5 approved rows
# must store (assured, core:assuredBy, assurance-activity). REL-01106 is
# asserted above via _emits_nothing: its assuredBy fact was removed and no
# substitute may be stored.
for rid in ("REL-00401", "REL-00719", "REL-00801", "REL-01269", "REL-01270"):
    fact = _stored(rid)
    check(f"control-case stored {rid} as {fact[1]}",
          fact in _fact_rowids and rid in _fact_rowids[fact],
          f"approved as core:assuredBy per Hamid 2026-09-26; expected stored fact {fact}")
# REL-01106's old fact must be gone entirely: no row may store the
# (CM-1-2-5-2, core:assuredBy, CM-1-2-5-4) triple.
check("control-case REL-01106 fact removed",
      ("CM-1-2-5-2", "core:assuredBy", "CM-1-2-5-4") not in _fact_rowids,
      "held for workbook correction; fact removed 2026-09-26")
# 2h. constrained-by control cases (Hamid verdicts 2026-09-26). Ten approved
# rows must store (constrained-thing, core:constrainedBy, constraint-source).
# All were already emitting: basis changes only. REL-00097 stays held.
for rid in ("REL-00015", "REL-00018", "REL-00024", "REL-00087", "REL-00091",
            "REL-00099", "REL-00103", "REL-00574", "REL-00894", "REL-01284"):
    fact = _stored(rid)
    check(f"control-case stored {rid} as {fact[1]}",
          fact in _fact_rowids and rid in _fact_rowids[fact],
          f"approved as core:constrainedBy per Hamid 2026-09-26; expected stored fact {fact}")
check("control-case hold REL-00097", _emits_nothing("REL-00097"),
      "context hold retained per Hamid 2026-09-26: no stored triple")
# 2j. dependsOnOutputOf contradiction control cases (Hamid verdicts 2026-09-26).
# Retain one direction per pair; the reverse facts must be gone. Hard rule:
# zero reciprocal two-cycles across all canonical dependsOnOutputOf facts.
for rid in ("REL-00862", "REL-01029", "REL-01061"):
    fact = _stored(rid)
    check(f"control-case stored {rid} as {fact[1]}",
          fact in _fact_rowids and rid in _fact_rowids[fact],
          f"retained direction per Hamid 2026-09-26; expected stored fact {fact}")
for fact in (("CM-1-3-7-1-2", "core:dependsOnOutputOf", "CM-1-3-6-4-2"),
             ("CM-1-3-6-6-14", "core:dependsOnOutputOf", "CM-1-3-8-2-5"),
             ("CM-1-3-8-4-5", "core:dependsOnOutputOf", "CM-1-3-8-4-4")):
    check(f"control-case reverse fact absent {fact[0]}->{fact[2]}",
          fact not in _fact_rowids,
          "held reverse direction; fact removed 2026-09-26")
_dep = {(r["subject"], r["object"]) for r in cfacts if r["predicate"] == "core:dependsOnOutputOf"}
# 2l. S&T enables control cases (Hamid verdicts 2026-09-26). Two approved
# rows must keep their core:enabledBy facts. 2026-09-26 (G3-B5):
# REL-00489, REL-01124, REL-01174 — prior S&T approvals superseded under the
# nearness-only identity rule (Supersedes2026-09-26STApproval); S&T stored
# controls removed; all three are now no-fact hold controls (see the
# control-case hold list below).
for rid in ("REL-00433", "REL-01172"):
    fact = _stored(rid)
    check(f"control-case stored {rid} as {fact[1]}",
          fact in _fact_rowids and rid in _fact_rowids[fact],
          f"approved as core:enabledBy per Hamid 2026-09-26; expected stored fact {fact}")
# REL-00437: genuine 2026-09-26 S&T approval ("quality-screened spot options
# make coordinated purchases, sales, and exchanges operationally actionable;
# bounded: trading coordination on quality-screened choices, not
# directing/approving trades") SUPERSEDED by Hamid's same-day G3-B3 verdict
# (D:hamid-verdict / TargetIdentityUnconfirmed). The approval assumed the
# asserted target; the nearness-only identity rule requires source-backed
# target identity before any predicate verdict. The later row-level verdict
# is authoritative. Prior decision retained in provenance as superseded.
check("control-case hold REL-00437", _emits_nothing("REL-00437"),
      "must stay held (G3-B3 supersession of 2026-09-26 S&T approval): no stored triple")
# Thirteen held rows emit nothing. Two facts survive via independent approved
# evidence (REL-00214, REL-00447) with the disallowed evidence rows removed.
for rid in ("REL-00262", "REL-00458", "REL-01122", "REL-01129",
            "REL-00263", "REL-00440", "REL-00455", "REL-00712",
            "REL-00750", "REL-01064", "REL-01206",
            "REL-00129", "REL-00243", "REL-00304", "REL-00489",
            "REL-00728", "REL-01006", "REL-01016", "REL-01124",
            "REL-01174"):
    check(f"control-case hold {rid}",
          _emits_nothing(rid),
          "S&T enables hold 2026-09-26; no emitted triple")
# 2m. G1a duplicate-provenance rows (Hamid 2026-09-26). REL-00152 and REL-00436
# are held as enables (no independent triple) but attached as duplicate
# provenance on independently-evidenced uses-input facts. Each must appear
# only alongside an independent uses-input evidence row for the same fact.
for rid, fact, indep in (("REL-00152", ("CM-1-2-1-4", "core:dependsOnOutputOf", "CM-1-2-1-1-4"), "REL-00214"),
                         ("REL-00436", ("CM-1-2-5-2-3", "core:dependsOnOutputOf", "CM-1-2-5-1-4"), "REL-00447")):
    rids = _fact_rowids.get(fact, [])
    check(f"control-case provenance {rid}",
          rid in rids and indep in rids and all(v2d[_r]["verb"] == "uses-input" or _r == rid for _r in rids),
          "G1a duplicate-provenance attach 2026-09-26; independent uses-input fact retained")
for rid, fact in (("REL-00214", ("CM-1-2-1-4", "core:dependsOnOutputOf", "CM-1-2-1-1-4")),
                  ("REL-00447", ("CM-1-2-5-2-3", "core:dependsOnOutputOf", "CM-1-2-5-1-4"))):
    check(f"control-case fact preserved via {rid}",
          rid in _fact_rowids.get(fact, []),
          "independent approved evidence survives; G1a attach adds provenance only")

# 2n. G1a duplicate-merge control cases (Hamid verdicts 2026-09-26). Every G1a
# row must name at least one independent uses-input row for the same directed
# fact; the fact must exist with that independent evidence; no G1a row may be
# the sole evidence for its fact; no new fact may be created by a merge.
g1a = list(rows("review-evidence/enables-g1a-duplicate-review-batch.csv"))
check("G1a batch has 77 approved rows", len(g1a) == 77, str(len(g1a)))
for g in g1a:
    rid, partners = g["row_id"], [x for x in g["merged_with_rows"].split(";") if x]
    fact = tuple(g["canonical_fact"].split())
    check(f"G1a {rid} names uses-input partner",
          partners and all(v2d[p]["verb"] == "uses-input" for p in partners),
          g["merged_with_rows"])
    check(f"G1a {rid} fact survives on independent evidence",
          fact in _fact_rowids and all(p in _fact_rowids[fact] for p in partners)
          and rid in _fact_rowids[fact],
          g["canonical_fact"])
    check(f"G1a {rid} not sole evidence for its fact",
          any(x != rid for x in _fact_rowids.get(fact, [])),
          "an independent uses-input row must remain if the enables mention is removed")
    check(f"G1a {rid} target_match recorded",
          g.get("target_match", "").strip() in (
              "stable-id (identity confirmed)",
              "label-match-only (identity-unconfirmed provenance)"),
          "census 2026-09-26: how the target was matched")

# 2o. G2 disguised-sequence verdicts (Hamid 2026-09-26). The 13 approved rows
# emit no core:enabledBy fact; the independently recorded sequence fact is
# preserved and the enables assertion is kept as non-emitting evidence.
# 2026-09-26 (G3-B5): the two row-level exceptions (REL-00129, REL-00728)
# are superseded under the nearness-only identity rule
# (Supersedes2026-09-25Review32Approval); the exception goes too. Their
# enables facts are absent; the independently recorded sequence facts stay
# (they are supported by REL-00131 and REL-00734, not by these rows).
g2 = list(rows("review-evidence/enables-g2-disguised-sequence-review-batch.csv"))
check("G2 batch has 15 rows with recorded verdicts",
      len(g2) == 15 and all(x["Hamid_decision"].strip() for x in g2), str(len(g2)))
for rid in ("REL-00122", "REL-00135", "REL-00174", "REL-00216", "REL-00375",
            "REL-00698", "REL-00727", "REL-00731", "REL-00955", "REL-00983",
            "REL-00992", "REL-01024", "REL-01090"):
    check(f"G2 {rid} emits no enabledBy fact",
          _emits_nothing(rid),
          "NoSeparateEnablesFact 2026-09-26; sequence fact already recorded")
for rid in ("REL-00129", "REL-00728"):
    fact = _stored(rid)
    check(f"G2 exception {rid} emits no enabledBy fact",
          fact[1] == "core:enabledBy" and fact not in _fact_rowids,
          "superseded 2026-09-26 (G3-B5); enables fact absent; sequence fact kept")
# Their sequence facts must stay present (supported by REL-00131/REL-00734).
for rid, pred in (("REL-00131", "core:precedes"), ("REL-00734", "core:precedes")):
    fact = _stored(rid)
    check(f"G2 sequence fact behind {rid} present",
          fact[1] == pred and fact in _fact_rowids and rid in _fact_rowids[fact],
          f"REL-00129/REL-00728 supersession removes only the enables fact, not the sequence fact")

# 2p. G1b no-verb-change verdicts (Hamid 2026-09-26). The 28 previously
# emitting rows must support no triple at all; their stored
# core:dependsOnOutputOf facts were removed (Rule 11: enables with only
# reverse informed-by evidence cannot emit dependsOnOutputOf). REL-01224
# (already context-held) emits no fact. REL-00489's "keep approved enabledBy"
# listing is superseded 2026-09-26 (G3-B5) — no fact, no-fact hold control;
# REL-00469 stays non-emitting.
for rid in ("REL-00140", "REL-00499", "REL-00565", "REL-00648", "REL-00679",
            "REL-00709", "REL-00732", "REL-00973", "REL-00974", "REL-00977",
            "REL-01108", "REL-01112", "REL-01148", "REL-01151", "REL-01154",
            "REL-01181", "REL-01184", "REL-01191", "REL-01194", "REL-01197",
            "REL-01213", "REL-01225", "REL-01230", "REL-01233", "REL-01234",
            "REL-01273", "REL-01296", "REL-01315", "REL-01224"):
    check(f"G1b {rid} emits no triple",
          _emits_nothing(rid),
          "HOLD / D:hamid-verdict / G1bNoVerbChange 2026-09-26; no substitute predicate")
for fact in (("CM-1-1-7-3-1", "core:dependsOnOutputOf", "CM-1-1-7-3-3"),
             ("CM-1-2-7-2-3", "core:dependsOnOutputOf", "CM-1-2-7-2-1"),
             ("CM-1-3-2-1", "core:dependsOnOutputOf", "CM-1-3-1-6"),
             ("CM-1-3-3-2-2", "core:dependsOnOutputOf", "CM-1-3-3-2-3"),
             ("CM-1-3-5-2", "core:dependsOnOutputOf", "CM-1-3-3-5-1"),
             ("CM-1-3-4-1-1", "core:dependsOnOutputOf", "CM-1-3-4-1-2"),
             ("CM-1-3-4-4-6", "core:dependsOnOutputOf", "CM-1-3-4-4-3"),
             ("CM-1-3-7-3-1", "core:dependsOnOutputOf", "CM-1-3-7-4-3"),
             ("CM-1-3-6-6-6", "core:dependsOnOutputOf", "CM-1-3-7-4-3"),
             ("CM-1-3-7-4-1", "core:dependsOnOutputOf", "CM-1-3-7-4-4"),
             ("CM-1-3-3-3", "core:dependsOnOutputOf", "CM-1-3-2-4"),
             ("CM-1-3-3-2-3", "core:dependsOnOutputOf", "CM-1-3-6-3"),
             ("CM-1-3-4-2", "core:dependsOnOutputOf", "CM-1-3-4-1"),
             ("CM-1-3-4-3", "core:dependsOnOutputOf", "CM-1-3-4-2"),
             ("CM-1-3-4-5", "core:dependsOnOutputOf", "CM-1-3-4-3"),
             ("CM-1-3-2-2", "core:dependsOnOutputOf", "CM-1-3-1-4"),
             ("CM-1-3-2-3", "core:dependsOnOutputOf", "CM-1-3-1-3"),
             ("CM-1-3-3-1", "core:dependsOnOutputOf", "CM-1-3-2-2"),
             ("CM-1-3-3-1", "core:dependsOnOutputOf", "CM-1-3-2-3"),
             ("CM-1-3-3-4", "core:dependsOnOutputOf", "CM-1-3-3-3"),
             ("CM-1-3-3-5", "core:dependsOnOutputOf", "CM-1-3-2-1"),
             ("CM-1-3-6-2", "core:dependsOnOutputOf", "CM-1-3-5-1"),
             ("CM-1-2-1-1-2", "core:dependsOnOutputOf", "CM-1-1-1-1"),
             ("CM-1-3-6-3", "core:dependsOnOutputOf", "CM-1-3-3-2"),
             ("CM-1-3-6-1", "core:dependsOnOutputOf", "CM-1-3-3-3"),
             ("CM-1-3-5-2", "core:dependsOnOutputOf", "CM-1-3-5-3"),
             ("CM-1-3-5-3", "core:dependsOnOutputOf", "CM-1-3-3-5"),
             ("CM-1-3-5-5-3", "core:dependsOnOutputOf", "CM-1-3-6-6")):
    check(f"G1b removed fact absent {fact[0]}->{fact[2]}",
          fact not in _fact_rowids,
          "silent dependsOnOutputOf fact removed 2026-09-26; uniqueness validated")
# G1b reconciled exclusions: REL-00489 approval superseded (G3-B5; already
# covered by the control-case no-fact hold list); REL-00469 non-emitting
# (already covered by the 2k hierarchy holds).

# 2k. hierarchy-hold control cases (Hamid verdicts 2026-09-26). Each held row
# must have zero emitted triples; none may be promoted via the hierarchy path.
for rid in ("REL-00002", "REL-00013", "REL-00466", "REL-00469", "REL-00764",
            "REL-00768", "REL-00773", "REL-00912", "REL-00923", "REL-00925"):
    check(f"control-case hold {rid}",
          _emits_nothing(rid),
          "hierarchy restatement; fact removed 2026-09-26; REL-01309 exception untouched")
# REL-01309 exception stays emitting under its original evidence marker.
check("REL-01309 remains emitting", not _emits_nothing("REL-01309"),
      "approved hierarchy exception; prior decision stands")

check("hard rule: zero reciprocal dependsOnOutputOf two-cycles",
      not any((o, s) in _dep for s, o in _dep),
      "no (A->B, B->A) pair may be emitted")
# Direction-table rules (Hamid 2026-09-26): no reciprocal two-cycles for
# core:precedes or core:governedBy either. A process cannot come both
# before and after another in the same lifecycle; governance runs one way.
_prec = {(r["subject"], r["object"]) for r in cfacts if r["predicate"] == "core:precedes"}
check("hard rule: zero reciprocal precedes two-cycles",
      not any((o, s) in _prec for s, o in _prec),
      "no (A->B, B->A) pair may be emitted")
_gov = {(r["subject"], r["object"]) for r in cfacts if r["predicate"] == "core:governedBy"}
check("hard rule: zero reciprocal governedBy two-cycles",
      not any((o, s) in _gov for s, o in _gov),
      "no (A->B, B->A) pair may be emitted")
# Answer 5 baseline (Hamid 2026-09-26): inverse properties may be declared
# for query and navigation, but materialized inverse triples are never
# written to the canonical facts store.
_inverse_preds = {"core:providesInputTo", "core:informs", "core:enables",
                  "core:constrains", "core:triggers", "core:follows",
                  "core:governs", "core:assures"}
_inverse_stored = [(r["subject"], r["predicate"], r["object"]) for r in cfacts
                   if r["predicate"] in _inverse_preds]
check("hard rule: zero stored triples using an inverse predicate",
      not _inverse_stored,
      f"inverse predicates are query-only; found {_inverse_stored[:3]}" if _inverse_stored else "")
# 2i. triggers control cases (Hamid verdicts 2026-09-26). Eighteen approved
# rows must store (triggered-activity, core:triggeredBy, trigger-activity).
# All were already emitting: basis changes only.
for rid in ("REL-00049", "REL-00127", "REL-00163", "REL-00169", "REL-00170",
            "REL-00235", "REL-00236", "REL-00246", "REL-00252", "REL-00291",
            "REL-00396", "REL-00398", "REL-00400", "REL-00403", "REL-00725",
            "REL-00892", "REL-00897", "REL-00901"):
    fact = _stored(rid)
    check(f"control-case stored {rid} as {fact[1]}",
          fact in _fact_rowids and rid in _fact_rowids[fact],
          f"approved as core:triggeredBy per Hamid 2026-09-26; expected stored fact {fact}")

# 3. canonical facts + contradictions
cf = cfacts
check("canonical-facts==716", len(cf) == 716, str(len(cf)))
check("canonical-facts-distinct", len({(r["subject"], r["predicate"], r["object"]) for r in cf}) == 716)

# Hamid 2026-09-26: nearness-only identity rule (G3-B1). A candidate
# resolved solely by label similarity, unique-candidate filtering,
# structural proximity, or other classifier nearness evidence cannot emit
# a semantic fact. It requires explicit target evidence or a separately
# recorded manual identity confirmation based on source material. The
# gate fails if a row whose target_identity_evidence is "NEARENESS ONLY"
# contributes a canonical relationship fact without a row-level identity
# override backed by source evidence.
# Hamid 2026-09-26: nearness-only identity rule (G3-B1, extended B2).
_rows_in_facts = set()
for _fr in cfacts:
    _rows_in_facts.update(x.strip() for x in _fr["row_ids"].split(";"))
_b1b2_violation = []
for _bfile in ("review-evidence/enables-g3-section-b1-review.csv",
               "review-evidence/enables-g3-section-b2-review.csv",
               "review-evidence/enables-g3-section-b3-review.csv",
               "review-evidence/enables-g3-section-b4-review.csv",
               "review-evidence/enables-g3-section-b5-class-verdict.csv"):
    _bb = {r["row_id"]: r for r in csv.DictReader(open(_bfile))}
    _held = [rid for rid, r in _bb.items()
             if "NEARENESS ONLY" in r.get("target_identity_evidence", "")
             and r.get("Hamid_decision", "").startswith("HOLD")]
    _b1b2_violation += [(_bfile.split("section-")[1].split("-")[0], rid)
                        for rid in _held if rid in _rows_in_facts]
check("g3-b1b2b3b4b5-nearness-identity-rule", len(_b1b2_violation) == 0,
      f"nearness-only identity violations (held B1/B2/B3/B4 row still contributes "
      f"a canonical fact): {_b1b2_violation if _b1b2_violation else 'none'}")
# B5 covers the 9 sweep supersessions + 33 class holds (all 42 now held).

cx = rows("contradictions.csv")
check("contradictions==0", len(cx) == 0, str(len(cx)))

# 4. no orphan row_ids
v2ids = {r["row_id"] for r in v2}
for fn in ["target-report/context-pass.csv", "requires-review.csv",
           "assures-review.csv", "enables-review.csv"]:
    rs = rows(fn)
    orphans = [r["row_id"] for r in rs if r["row_id"] not in v2ids]
    check(f"no-orphans {fn}", not orphans, str(orphans[:3]))
cf_orphans = []
for r in cf:
    for rid in r["row_ids"].split(";"):
        rid = rid.strip()
        if rid and rid not in v2ids:
            cf_orphans.append(rid)
check("no-orphans canonical-facts.csv", not cf_orphans, str(cf_orphans[:3]))

# 5. sample verdicts
txt = open("target-report/context-sample-review.md").read()
verdicts = re.findall(r"Verdict: (OK|FLAG)", txt)
check("sample-verdicts==51", len(verdicts) == 51, str(len(verdicts)))

# 6. label report
lab = rows("label-report/label-dispositions-v1.2.csv")
carried = [r for r in lab if r["row_status"] == "carried-over-approved"]
new = [r for r in lab if r["row_status"] != "carried-over-approved"]
check("label-rows==104", len(lab) == 104, str(len(lab)))
check("label-carried==90-approved", len(carried) == 90 and all(r["decision"] == "approve" for r in carried))
check("label-new==14 (all approved 2026-09-25)", len(new) == 14 and
      all(r["decision"] == "Approved" for r in new),
      f"{len(new)} new")

# 3b. G1b verb-change premise (added 2026-09-26): an enables row whose only
# reverse-pair evidence is informed-by must NOT be stored as
# core:dependsOnOutputOf. Storing it so changes the verb at emission
# (Rule 11): the source said "enables", the corroboration says
# "informed-by", and no independent uses-input evidence exists. Row-level
# Hamid verdicts approving a different predicate are the only exception.
from collections import defaultdict as _dd
_graph = _dd(set)
for _r in v2:
    _c = [c.strip() for c in _r["candidate_slugs"].split(" | ") if c.strip()]
    if len(_c) == 1 and _r["disposition"] in ("ResolvedToConcept", "SoleCandidate"):
        _graph[(_r["source_slug"], _c[0])].add(_r["verb"])
_v2d = {r["row_id"]: r for r in v2}
_viol = []
for _fr in cf:
    if _fr["predicate"] != "core:dependsOnOutputOf":
        continue
    for _rid in [x.strip() for x in _fr["row_ids"].split(";")]:
        _r = _v2d.get(_rid)
        if not _r or _r["verb"] != "enables":
            continue
        _c = [c.strip() for c in _r["candidate_slugs"].split(" | ") if c.strip()]
        if len(_c) != 1:
            continue
        _rev = _graph.get((_c[0], _r["source_slug"]), set())
        if "informed-by" in _rev and "uses-input" not in _rev:
            _viol.append(_rid)
check("g1b-no-verb-change", not _viol,
      f"{len(_viol)} enables rows stored as dependsOnOutputOf on informed-by-only reverse evidence: {sorted(_viol)[:5]}...")

print()
if fails:
    print(f"GATE FAILED: {len(fails)} check(s): {fails}")
    sys.exit(1)
print("GATE GREEN: all evidence-package consistency checks pass.")
