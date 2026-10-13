## Code Review Results

**Scope:** commit `0543e76` only (parent `5b86f8c`) on `release/core-1.0.0` (14 files, 250 lines). Not vs `main`.
**Intent:** Fix round-1 findings 1, 2, 5, 7: Destinations tests that read intake values from the source taxonomy, build `1.0.0-rc.1` with no `dcterms:issued`, mark EPM-DEC-001-0029 Proposed, one `dcterms:title`, and `--verify` matching `releases/core/1.0.0`.
**Mode:** markdown report-only, focused (correctness in this context plus one independent adversarial read)

**Reviewers:** correctness, adversarial
- adversarial -- silent-pass Destinations / `--verify` / public version stamp (in-process fallback)

### Claims checked

| Claim | Result |
|-------|--------|
| (1) Destinations reads each `intake:` value from the source and a swapped mapping fails | Partial. Literals, level, kind, APQC, labels, fact direction: yes. Q6 second facet, Q10 property choice, `parkedChildren`: no. |
| (2) `1.0.0-rc.1`, no `dcterms:issued` while STAGE is set; versionIRI, versionInfo, catalog, manifest use the rc label | True on the shipped package. The Destinations check compares to `b.LABEL` / `b.STAGE`, so `STAGE = None` still goes green. |
| (3) 0029 and README row say Proposed; no leftover Decided stamp | True. |
| (4) Ontology header has exactly one `dcterms:title` | True (`mod:core` in `core.ttl:17161`). |
| (5) `releases/core/1.0.0` matches `build_core.py --verify` | True (`release package is current`; 15079 triples, SHACL conforms). |

### P1 -- High

| # | File | Issue | Reviewer | Confidence |
|---|------|-------|----------|------------|
| 1 | `business_architecture/ontology/release/test_build_core.py:108` | Routing every terminology note to `dcterms:provenance` still passes Destinations | correctness, adversarial | 100 |
| 2 | `business_architecture/ontology/release/test_build_core.py:99` | Daily/weekly/monthly only assert cadence; a swapped operatingMode still passes | correctness, adversarial | 100 |
| 3 | `business_architecture/ontology/release/test_build_core.py:137` | Candidate check tracks `b.LABEL` / `b.STAGE`, so a premature 1.0.0 cut stays green | adversarial | 100 |

- **#1** -- Destinations XOR-checks provenance vs editorialNote, then only requires rename notes on provenance. Route every note to `dcterms:provenance` (ignore `note_kind`) and XOR stays true. Editorial and decision-pointer notes then miss Q10. Assert editorial/decision-pointer notes on `skos:editorialNote`. `requires_verification: true` (no cross-model receipt).

- **#2** -- Horizon table maps `daily` to `("cadence", "daily")` only and looks up `b.HORIZON_PROPERTY`. Q6 also requires operatingMode periodic. Change `HORIZON["daily"]` to `continuous` plus cadence daily: facet count stays 2, Destinations still finds cadence/daily, conservation still balances. Keep a test-local 0029 table and assert both facets. `requires_verification: true`.

- **#3** -- `versionInfo == b.LABEL` and `issued` is checked only `if b.STAGE is not None`. Set `STAGE = None` and `ISSUED` to a date: Destinations and `--verify` still pass on dated 1.0.0. Assert the literals `1.0.0-rc.1` and absent issued independently of `b.LABEL`. The shipped graph, catalog, and manifest already use `1.0.0-rc.1` and have no issued date. `requires_verification: true`.

### P2 -- Moderate

| # | File | Issue | Reviewer | Confidence |
|---|------|-------|----------|------------|
| 4 | `business_architecture/ontology/release/test_build_core.py:55` | Destinations never reads `intake:parkedChildren` | adversarial | 100 |

- **#4** -- Five `parkedChildren` triples exist. Remap them to `keyInputFlow` (assertIn, not exclusive) and Destinations stays green. Assert each split value on `core:plannedChildNote`.

### Actionable Findings

| # | File | Issue | Route | Notes |
|---|------|-------|-------|-------|
| 1 | `test_build_core.py:108` | Pin Q10 destinations, not XOR | `manual -> downstream-resolver` | `suggested_fix` present |
| 2 | `test_build_core.py:99` | Assert both Q6 facets for daily/weekly/monthly | `manual -> downstream-resolver` | `suggested_fix` present |
| 3 | `test_build_core.py:137` | Pin `1.0.0-rc.1` and no issued without `b.LABEL` | `manual -> downstream-resolver` | Shipped package already matches |
| 4 | `test_build_core.py:55` | Assert `parkedChildren` on `plannedChildNote` | `manual -> downstream-resolver` | `suggested_fix` present |

### Coverage

- Focused path. No other reviewer agents. No validator.
- Independent adversarial read: in-process fallback. Codex then Claude both reported transport unavailable (pre-egress, route): `acpx` exited 1 before sending the prompt. No reviewed content left the machine. `independence_verified: false`. Local adversarial is same serving family; agreement does not promote confidence.
- Criteria: `AGENTS.md` (instruction-file fallback; no `CODING_STANDARDS.md`). 0029 is Proposed. Attestation, ledger approval, and release approval stay open.
- Compound Packs: not applied.
- Not assessed: learnings, agent-native gaps, deployment notes.
- Residual risks: `--verify` still diffs this generator against itself; DCAT download URLs use `/releases/{LABEL}/` while files sit in `releases/core/{VERSION}/`.
- Testing gaps: `holdReason` / `owl:deprecated` on the two status rows; cross-functional `skos:note`; title guard is a count of one, not the playbook string.

**How this can pass review and still be wrong.** Destinations, conservation `5571=5571`, SHACL, `--verify`, Proposed, and a single title can all be green while (a) every terminology note sits on `dcterms:provenance`, (b) daily concepts carry the wrong operatingMode, (c) `parkedChildren` land on a flow predicate, and (d) someone sets `STAGE = None` and ships dated 1.0.0 because the candidate test tracks `b.LABEL`.

---

> **Verdict:** Ready with fixes
>
> **Reasoning:** Claims 2 (on disk), 3, 4, and 5 hold. Claim 1 does not: Destinations still misses Q10's property, Q6's second facet, and `parkedChildren`. Not MERGE-READY until those tests fail a swapped mapping.
>
> **Fix order:** Pin Q10 destinations (#1), then Q6 dual facets (#2), then `parkedChildren` (#4), then pin `1.0.0-rc.1` without `b.LABEL` (#3).
