# Step 9 walkthrough: controlled values and evidence on canonical facts

Prepared for Hamid on 2026-10-14. This package decides nothing. It sets out the two things EPM-DEC-001-0035 leaves for you, in its section "For Hamid: evidence on the facts" (lines 25 to 29).

Figures come from repo commit `6baf510` (`python3 scripts/epm_facts.py counts`) and from running the shapes with pySHACL against `business_architecture/ontology/releases/core/2.0.0/core.ttl`. Paths below are relative to `business_architecture/ontology/` unless they start with `business_architecture/` or `scripts/`.

## What you need to do

Reply with two answers, for example "1a, 2a".

1. Approve the eleven controlled-value shapes in `validation/controlled-values.ttl`. Recommended: 1a, approve them as written.
2. Choose how canonical facts carry their evidence in the next `core` release. Recommended: 2a, add one evidence node per canonical fact and keep the direct triple.

## What changed since EPM-DEC-001-0035

EPM-DEC-001-0035 was written against `core` 1.0.0. Since then `core` 2.0.0 was released on 2026-10-13 (`releases/core/CHANGELOG-2.0.0.md`). Its shapes do not include the controlled-value shapes, although 0035 decision item 2 says they "join the release shapes at the next `core` release". EPM-DEC-001-0038 line 33 also left the evidence nodes out of 2.0.0 to wait for this walkthrough. Both asks now apply to the release after 2.0.0.

## Question 1. Approve the controlled-value shapes

Each shape takes every value of one property and requires it to be a concept in one named list. In RDF terms, the value must carry `skos:inScheme` with that list. The 2.0.0 release shapes check only that seven of these values are some SKOS concept (`releases/core/2.0.0/shapes.ttl`, lines 27 and 34 to 39). A value from the wrong list therefore passes the release.

I tested this. I changed the operating mode of CM 1.1.1.1.1 to the cadence "Monthly". The 2.0.0 release shapes accept the change. `validation/controlled-values.ttl` rejects it with this report:

```
Constraint Violation in HasValueConstraintComponent
  Focus Node: cad:monthly
  Result Path: skos:inScheme
  Message: An operating mode comes from the operating mode list.
```

The unchanged `core` 2.0.0, with the organization module's vocabulary and RACI assignments, has zero violations. The repo test runs the same shapes on `core` 1.0.0 and also finds zero.

One line per shape, from `validation/controlled-values.ttl` (lines 12 to 56). The last column counts how many times `core` 2.0.0 or the organization assignments use the property.

| Property | Each value must be in | Values in the list | Uses |
|---|---|---|---|
| APQC mapping decision | APQC mapping decision list | 5: Adopted, No candidate, No source, Rejected, Review link | 500 |
| Operating mode | Operating mode list | 3: Continuous, Event-driven, Periodic | 414 |
| Cadence | Cadence list | 5: Annual, Daily, Monthly, Quarterly, Weekly | 92 |
| Planning level | Planning level list | 3: Operational, Strategic, Tactical | 71 |
| Lifecycle status | Lifecycle status list | 3: Active, Deprecated, Retired | 1 |
| Governance status | Governance status list | 5: Approved baseline, Candidate, Draft, Exploratory, Implemented | 0 |
| Hold status | Hold status list | 5: Decision hold, Evidence hold, Implementation hold, No hold, Ownership hold | 1 |
| Concept kind | Concept kind list | 3: Capability, Process, Structural anchor | 488 |
| RACI level (organization module) | RACI level list | 4: Accountable, Consulted, Informed, Responsible | 940 |
| Evidence basis | Evidence basis list (`core:EvidenceBases`) | 2: Reference-model assumption, Source-confirmed | 17 |
| Sequence scope | Scope unit list (`core:ScopeUnits`) | 10: Delivery period, Demurrage claim, Forecast version, Physical movement, Plan-selection decision, Posting, Quote version, Replenishment requirement, Scheduling horizon, Transaction | 17 |

Three rows need a note. The release already checks concept kind against its three values with `sh:in` (`releases/core/2.0.0/shapes.ttl`, line 26), so that shape adds no new check. The release has no shape for evidence basis or sequence scope; build-time shapes in `step4/scoped-sequence/` check them (EPM-DEC-001-0035, Context). Governance status has no values in the graph, so its shape checks nothing today.

There are two gaps you should know about before you answer. First, `validation/test_controlled_values.py` loads `core` 1.0.0 (line 21), not 2.0.0. Second, 2.0.0 added a new code list, `core:businessDomain`, with 7 values. `controlled-values.ttl` has no shape for it. The 2.0.0 release shapes check it instead (`releases/core/2.0.0/shapes.ttl`, lines 79 to 89). The test that fails when a code-list property has no shape cannot see this, because it reads 1.0.0.

Options:

- 1a (Recommended). Approve the shapes as written. Core 2.0.0 conforms, and each shape except concept kind closes a gap the release shapes leave open. What happens: I record your words in EPM-DEC-001-0035 in a PR. The same PR points the test at `core` 2.0.0, so the completeness test covers the business domain list. The shapes join the release shapes of the next `core` release.
- 1b. Approve with changes. Name the change, and I make it in a PR before the shapes join a release.
- 1c. Do not approve. The shapes stay a `scripts/check.sh` check only. The release shapes keep accepting a value from the wrong list.

## Question 2. How canonical facts carry their evidence

`core` 2.0.0 holds 640 canonical facts. Each is a direct triple between two processes, using one of nine predicates. Their evidence is 812 relationship-workbook rows (REL IDs). Those rows sit in `releases/core/1.0.0/canonical-facts.csv`, not in the graph. 172 of the 640 facts rest on two or more rows. The 2.0.0 package has no copy of that file, because it was built from the 1.0.0 graph (`releases/core/2.0.0/manifest.json`, `built_from`).

The first Step 9 shape is "every relationship fact links to its source evidence" (EPM-DEC-001-0014; `ontology-playbook.md`, Step 9). Today all 640 facts would fail it. The 17 scoped-sequence nodes already pass, because each carries its row in `core:sourceRow`. For example, `seq:CM-1-1-1-1-4--CM-1-1-2--forecast-version` carries `REL-00008`.

### A real fact, before and after

`scripts/epm_facts.py row REL-00001` reports that REL-00001 stores the fact "CM-1-1-1-1-1 core:precedes CM-1-1-1-1-2". The CSV gives two rows for it, REL-00001 and REL-00003. CM 1.1.1.1.1 is "Prepare Master Data To Create Demand Forecast" and CM 1.1.1.1.2 is "Develop Statistical Baseline".

Today, in `releases/core/2.0.0/core.ttl` (line 371), the graph holds only the triple:

```turtle
proc:CM-1-1-1-1-1 core:precedes proc:CM-1-1-1-1-2 .
```

Under option 2a, the triple stays and one node is added:

```turtle
proc:CM-1-1-1-1-1 core:precedes proc:CM-1-1-1-1-2 .

fact:CM-1-1-1-1-1--precedes--CM-1-1-1-1-2 a core:CanonicalFact ;
    core:factSubject   proc:CM-1-1-1-1-1 ;
    core:factPredicate core:precedes ;
    core:factObject    proc:CM-1-1-1-1-2 ;
    core:evidenceRow   "REL-00001", "REL-00003" .
```

The class, property and namespace names are placeholders for the PR to settle. The node cannot reuse `core:sourceRow` as it stands. That property's domain is `core:ScopedSequence` (`releases/core/2.0.0/core.ttl`, lines 327 to 331), so a reasoner would type every fact node as a scoped sequence.

Under option 2b, the first line is removed and the node is the only record of the fact.

### Options

- 2a (Recommended). Add one node per canonical fact and keep the direct triple. This is the qualified-relation pattern you adopted in EPM-DEC-001-0020 (decision item 3), and it changes nothing that current queries read. The cost is 640 nodes and about 3,372 triples (640 times four, plus 812 row values) on the 16,200 triples of 2.0.0. It only adds terms, so it is a minor release under the playbook's Appendix B (`ontology-playbook.md`, line 1300), most likely `core` 2.1.0. The module policy gives minor releases to the module owner (EPM-DEC-001-0037, line 12); your answer here sets the pattern. Two follow-on changes come with it. The projection's Rule 4a check must name the new class (`projection/pipeline.py`, lines 119 to 121), and Neo4j gets 640 more nodes. The risk is that the triple and the node drift apart, so the evidence-link shape would require exactly one node for each direct triple, and the reverse.
- 2b. Add the node and drop the direct triple. This removes triples that queries read, so it is a major release under Appendix B (lines 1292 to 1298), `core` 3.0.0, which needs your approval. It breaks the competency query for Q39 (`regression/queries/q39-downstream.rq` reads the direct triples) and the projection's process-to-process edges. You said "No one uses the ontology yet" (`step4/review-evidence/hamid-answers/core-2-0-0-release.md`), so the cost to consumers is low today. The cost to this repo's own queries and projection is not.
- 2c. Keep the evidence in the CSV and check it with a script. EPM-DEC-001-0035 rejected this as the Step 9 shape, because the rule is that the graph itself links each fact to its evidence. What happens: the first Step 9 rule is never checked in the graph, and the playbook's Step 9 "Done when" needs a recorded exception.
- 2d. Wait. Nothing changes, and the evidence-link shape stays unbuilt.

### What an answer unblocks

Option 2a or 2b unblocks the Step 9 evidence-link shape, the first of the three shape sets in EPM-DEC-001-0014 (see also `validation/README.md`, line 8). It also lets a graph user find the source rows for a link without the CSV.

No competency question waits on this. In `regression/expected.csv`, no question names evidence on relationship facts. Q44 is the closest, and its open part is "marking which source is authoritative" for a definition (line 45). Evidence rows on relationship facts do not answer that.
