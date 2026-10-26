# EPM-DEC-001-0098: Dispositions for the qSKOS findings on the released modules: preferred labels shared across schemes are accepted, and every other finding is fixed in its module's next release

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-25, for accepting preferred labels shared across schemes; the other dispositions delegated under EPM-DEC-001-0028); one question open, listed below |
| Date | 2026-10-25 |
| Questions | Step 3's rule for checks adopted after release: what happens to each finding the `ontology` skill's qSKOS checks make on the newest release of each module? Should EPM rename the seven preferred labels it shares across schemes, or should the skill exempt them? |
| Source | Claude Code session of 2026-10-25; `answers-2026-10-25-qskos.md` |

## Context

personal-agent-skills #53 added the qSKOS quality issues that an offline build can check to the `ontology` skill's `check_taxonomy.py`. The ontology playbook's Step 3 says: "When you adopt a check on modules already released, record what it finds in them and give each finding a disposition by recorded decision (fix it in the next release, or accept it with a reason); a finding in new work blocks the gate." EPM's modules do not run the skill's checker, so nothing failed, but the worklog recorded that this build did not yet meet that part of the gate (`ontology-worklog.md`, the Step 3 "Done when" row of the evidence for the skill capabilities added on 2026-10-24 and 25).

On 2026-10-25 Claude reran the checker read-only on the newest release of each of the eleven modules (core 2.3.0, data-product 1.1.0, integration 2.0.0, kpi 1.1.1, lane 1.0.0, market-data 1.0.0, organization 2.0.0, party 1.1.0, ref-mpc 1.2.0, system 1.0.0, value-stream 1.1.0), once per module. It ran the checker as of #53 and as of personal-agent-skills #69, merge `056d984`, which exempts the shared preferred labels. Counted as before, findings new with #53 only, it found:

| Check (qSKOS issue) | Findings | Where |
|---|---|---|
| `scheme` (Omitted Top Concepts) | 27 | 10 modules; every one is a flat code list, and no member is stated as a top concept |
| `reciprocal` (Unidirectionally Related Concepts) | 109 | party 106, across 19 schemes; data-product 3, the segments in `dp:DataProducts`. Each is a `skos:topConceptOf` with no `skos:hasTopConcept` the other way |
| `collision` (Overlapping Labels) | 11 | 7 preferred labels shared across schemes; 4 alternative labels in core that equal another concept's preferred label |
| `disjoint-labels` (Disjoint Labels Violation) | 1 | kpi, `measure:rm-margin-indicator` |
| `uri-scheme` | 0 | |

The worklog recorded 28 `scheme` findings. Both versions of the checker find 27 on the same releases, so 27 is the count this record uses, and the worklog row gets a dated note.

## Decision

**The decision owner's decision:** accept the preferred labels EPM shares across schemes. Claude asked whether EPM should rename the seven, or the skill should exempt shared labels, and recommended exempting them "when each scheme is a different view", with same-scheme collisions still failing. The decision owner: "I agree . But can you explain why this is the best route." The skill now carries the exemption (personal-agent-skills #69, merge `056d984`).

**The dispositions (Claude, under EPM-DEC-001-0028, from the skill's own rules):**

1. **Seven preferred labels shared across schemes: accepted, no change.** Finance, IT Services, Marketing and Refining are each a business domain (`core:BusinessDomain`) and a process (the `mod:core` scheme) in core. Asphalt is a line of business and a product, Cardlock a line of business and a site type, and Prospect a lifecycle stage and a system stage, in party. Each label is the right business term in its scheme, and identity is the IRI. The checker as of #69 no longer reports them.
2. **Four alternative labels in core: fixed in core's next release.** The process map gives two pairs of processes the same names, and core 2.3.0 renamed the second pair's preferred labels, keeping the process map's name as an alternative label. Each alternative label now equals the other concept's preferred label:

   | Concept | Alternative label | The same text is the preferred label of |
   |---|---|---|
   | CM-1-3-2-3-1 Test Consumer Value Proposition | Test Customer value proposition | CM-1-3-2-2-1 |
   | CM-1-3-2-3-2 Formulate and Evaluate Consumer Value Proposition Alternatives | Formulate and Evaluate Strategic Operating Alternatives (CVP) | CM-1-3-2-2-2 |
   | CM-1-3-2-3-3 Establish Consumer Value Proposition Principles and Objectives | Establish CVP principles and objectives | CM-1-3-2-2-3 |
   | CM-1-3-2-3-4 Develop and Update Consumer Value Proposition Strategy | Develop/Update Strategy (CVP) | CM-1-3-2-2-4 |

   The next core release moves each of these names from `skos:altLabel` to a history annotation, so the process map's name is still recorded. The skill makes an earlier name an alias "only if it is unique, accurate and useful" and keeps "other former names in a history annotation" (`identity-taxonomy.md`, Step 2, rule 8): a search on a shared alias finds two processes.
3. **One disjoint-labels finding in kpi: fixed in kpi's next release.** `measure:rm-margin-indicator` has "R&M Margin Indicator" as both its preferred and an alternative label, which SKOS forbids (SKOS Reference, integrity condition S13). The next kpi release drops the alternative label. That release is already planned for item F (EPM-DEC-001-0097, the narrowing of Additional Market Prices).
4. **109 one-way top concepts: fixed in party's and data-product's next releases.** Each scheme states `skos:hasTopConcept` for every concept that states `skos:topConceptOf` it. The meaning does not change, since SKOS defines the two as inverses.
5. **27 schemes with no top concept: fixed in each module's next release.** Each of these code lists is flat: no member has a parent in its scheme. The next release states every member as a top concept, both ways:
   - core: `core:ApqcMappingDecision`, `core:BusinessDomain`, `core:Cadence`, `core:ConceptKind`, `core:EvidenceBases`, `core:GovernanceStatus`, `core:HoldStatus`, `core:LifecycleStatus`, `core:OperatingMode`, `core:PlanningLevel`, `core:ScopeUnits`;
   - data-product: `dp:PortfolioStatus`;
   - integration: `auth:EvidenceTier`, `con:RuleKind`, `plc:PlacementKind`;
   - kpi: `kpi:MeasureKind`, `kpi:Measures`;
   - lane: `lane:OfficeLanes`;
   - market-data: `mkt:BenchmarkKind`, `mkt:MarketRegions`, `mkt:RefiningRegions`, `mkt:Series`;
   - organization: `orgm:RaciLevel`;
   - party: `party:customer-systems`;
   - system: `sys:SystemKind`, `sys:Systems`;
   - value-stream: `vs:MeasureRelationship`.

   The skill treats a code list as "a flat scheme of top concepts by design" (`quality.md`, "The qSKOS issues").

Each release that carries one of these fixes runs the skill's `check_taxonomy.py` on its own module, and the fixed findings must be gone. None of these fixes changes an IRI or a definition.

## Open

- **Preferred labels shared inside one scheme.** The same run reports 11 of them, found by the per-scheme collision check that predates #53, so the trial did not count them as new. Seven are in core's process scheme, where the process map gives processes under different parents the same name (Actualizations, Analyze Data, Define Analysis Objectives & Scope, Determine Taxability, Document Findings, Obtain latest XPIMS MOP model, Source & Collect Information). Four are in `dp:DataProducts`, where a data-product line and a product share a short label (HR, IT, S&BD, SC). This record gives them no disposition. Renaming a process's label means a process-map proposal (`business_architecture/business_process/` is the authority). *2026-10-25 (evening):* under the delegation's amendment of that evening, Claude decides the four in `dp:DataProducts` in item F's `data-product` release, and lists the seven in core's process scheme in the night's report as a candidate process-map proposal.

## Alternatives considered

- **Rename the seven shared preferred labels in EPM.** Not chosen by the decision owner. Each is the right term in its own scheme, and a qualifier would make a business term read like a technical one.
- **Accept the other findings with a reason instead of fixing them.** Not chosen: each fix adds or moves a statement without changing any meaning, and each finding is one the skill's checks fail in new work.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-25-qskos.md`: "I agree . But can you explain why this is the best route."

## Evidence

- The newest release of each module under `business_architecture/ontology/releases/`.
- `check_taxonomy.py` in the `ontology` skill as of personal-agent-skills #53 (merge `4dc0d91`) and #69; `references/quality.md`, "The qSKOS issues"; `references/identity-taxonomy.md`, Step 2, rule 8.
- `business_architecture/business_process/downstream_process_map.json`, the names of CM 1.3.2.2 and CM 1.3.2.3's subprocesses.
- W3C, *SKOS Simple Knowledge Organization System Reference*, Recommendation, 18 August 2009, https://www.w3.org/TR/skos-reference/: S13 (the preferred, alternative and hidden labels are pairwise disjoint) and the inverse pair `skos:hasTopConcept` and `skos:topConceptOf`.
