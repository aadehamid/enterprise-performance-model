# EPM-DEC-001-0112: The follow-up release: a technical-graph vocabulary module, peer names kept in market news, preflight refusing Databricks without AuraDB, and content-only walkthrough changes

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-11-02, for the ten points below; the build choices delegated under EPM-DEC-001-0028; the module's `1.0.0` stays with the decision owner) |
| Date | 2026-11-02 |
| Questions | Claude asked ten questions in two rounds, each with a recommendation, to open the follow-up release that EPM-DEC-001-0110 plans |
| Source | Claude Code session of 2026-11-02; `answers-2026-11-02-follow-up-release.md`, blocks 1 to 8 |

## Context

EPM 1.0 was cut from `main`, published as `share/epm-1.0` in the private release repository, and every store was reloaded from it. The decision owner confirmed it on 2026-11-02 (block 6). EPM-DEC-001-0110 plans a second release, the full version, after three pieces of work: a vocabulary module for the technical graph, lineage from Databricks (#457) and the in-sync plan (#455, #426). The plan (`release-cut/PLAN.md`, "After the first release"; a local file outside the repository, as EPM-DEC-001-0110 says) says the module's competency questions are "locked by the owner" and its `1.0.0` needs the decision owner's approval.

The demo's technical graph (`demos/downstream-pricing-databricks-free/graph/tech-graph.ttl`) uses 13 node kinds and 23 properties in the demo's own namespace, `urn:pricing-demo:tech-vocab#` (the release tooling also writes it, in `scripts/share_release/stores.py`). The demo's decision trail, `graph/decision-trail.ttl`, uses the same namespace for its own terms. Its node kinds name a layer (`SilverTable`, `GoldTable`), and it records no owner.

## Decision

**The decision owner's decisions** (block 1: "yes to all." to Q1 to Q9, with Q7 answered further in block 1; block 2 to Q10; block 3, "yes, go ahead", to the summary of all ten points, which added point 10. The numbers below are points of that summary, not question numbers: point 7 holds Q7 and Q10):

1. **The competency questions,** locked as written: where does this number come from; can I trust it today (last refresh, checks passed); what is affected if this table or system changes; is it built as designed; who answers for it; which agent or report answers for this measure.
2. **Neutral classes.** The module defines classes for the kinds of thing (a data object, a view, a metric view, a pipeline step, a quality check, an agent, a source system, a host), and the layer (bronze, silver, gold) is a value from a code list. The demo's 13 kinds map onto them.
3. **Who answers for it** is found by following a node's `designedAs` link to its data product, and from there to the accountable role in `organization`. The module adds no owner property.
4. **The module** is named `technical-graph`, with its terms under `https://w3id.org/lsc/ontology/modules/technical-graph/`. A small example graph cut from the demo's graph ships with it as test data, not as ontology content, and the regression runs the six questions on the module plus that example. The demo moves from `tv:` to the module's terms, so the live graph meets the same shapes.
5. **Stores.** The module's vocabulary loads into all four stores, `epm_triples` included, like every module. The technical graph's records (nodes, refresh times and check results) stay out of `epm_triples`; its Delta copy stays as it is (EPM-DEC-001-0110, decision 14 and "What follows", item 9).
6. **The `1.0.0` approval.** The decision owner owns the module. Claude builds it as a candidate through its pull requests and sends the decision owner one page with the terms, the six questions and their results on the example. The release is `1.0.0` when the decision owner replies to approve it, and that reply is recorded word for word.
7. **Peer names in market news stay; the ontology still names no peer.** The decision owner (block 7): "by the way no peer name in the ontology though as discussed. just wants to make sure". Point 7 reaches only the demo's market news; every ontology module keeps EPM-DEC-001-0110's rule, with peer evidence read as industry view. "if this is from the Decision API search for what is going on in the market at the time, we should leave them in". Sunoco appears in the cached Parallel search results under `data/parallel/`; BP, Shell and Chevron appear in `SCENARIO.md`, the decision owner's briefing collection on the market in October 2026. Both stay, and the release README's statement that no peer is named is to be reworded, in the follow-up release, to say peers are named only in market news; the rewrite rules and the leak gate are to leave market news in place: "yes, keep them and reword the README line." In the same message the decision owner asked what the scenario's briefings are; Claude answered (six dated executive briefings on North American downstream markets, October 5 to 23, 2026, whose figures calibrate the demo's synthesized data) before the summary that block 3 approved.
8. **Preflight refuses Databricks without AuraDB.** Choosing Databricks without AuraDB failed tech-compare on a fresh copy; `rebuild_stores.py`'s preflight refuses that choice before any work starts, with a message that says to add AuraDB.
9. **The walkthrough** gets the content changes this release needs, such as the new module and the in-sync steps, and no design pass.
10. **Question 17** (EPM-DEC-001-0086) is asked again before anything is shared.

**The run.** The decision owner set the work as a goal and approved its brief: "Goal set: treat the plan as agreed on as a goal until done. use /night-run as well", then "Approve, start (Recommended)". Choices made in the run are delegated under EPM-DEC-001-0028 and logged.

## Alternatives considered

- **Copy the demo's 13 kinds one for one.** Rejected: names that hard-code a layer tie the vocabulary to one demo.
- **An owner property on technical nodes.** Rejected: ownership is defined in `organization`, and a second owner field could disagree with it.
- **Keep the vocabulary out of `epm_triples` too.** Rejected: the vocabulary is definitions, like every module; the decision owner's words of 2026-10-31 ("the technical graph should not be projected to Databricks since databrick already have technical graph in delta table") are read as covering the graph's records.
- **Remove the peer names from the demo.** Rejected by the decision owner for market news.

This supersedes, for market news, EPM-DEC-001-0110's amendment item 4 (rewrite the peer names in the cached Parallel answers), its "What follows" item 3 (the peers item), the leak gate's clause in its "What follows" item 1, its Context's "no peer may be named", and the peers bullet of its amendment of 2026-10-31 (later); its decision 2, which says how peer claims are termed (industry view), stands, because peer claims outside market news are unchanged. It also settles the call EPM-DEC-001-0111, item 20, left open. Each statement superseded or settled carries a dated note.

## The decision owner's recorded words

> yes to all.
>
> Q7 if this is from the Decision API search for what is going on in the market at the time, we should leave them in

> yes, keep them and reword the README line.

> yes, go ahead

> Goal set: treat the plan as agreed on as a goal until done. use /night-run as well

> Confirm EPM 1.0 (Recommended)

> by the way no peer name in the ontology though as discussed. just wants to make sure

## Consequences

- The technical-graph module is the first test of the `ontology` skill's `references/new-module.md`, which is adjusted so a module can pass on its package plus a conforming example.
- The demo's technical graph, its loader and its checks move to the module's terms; the lineage, in-sync and release work that follows builds on them.
- The follow-up release is cut once the module exists, and replaces EPM 1.0 as `share/epm-1.0`.

## Amendment, 2026-11-02 (later): technical-graph 1.0.0, the store secrets and the drift check

The decision owner's answers (block 8), to three questions Claude asked during the build:

1. **technical-graph 1.0.0 is approved:** "1. approve 1.0.0", to the one page with the module's terms, its six questions and their results on the example graph (item 6). The candidate of #468 is released as `1.0.0`, a major the decision owner approved.
2. **The store logins become GitHub secrets (#426):** "2. Yes we should do do this . I want to know how to do this as well". Claude sets the six AuraDB and Databricks secrets from the local login files without printing them; the seventh, `EPM_SKILLS_TOKEN`, is a read-only token for the skills repository that only the decision owner can create.
3. **The drift check stays manual (#455):** "3. Aligned on #455", to the recommendation to make `sync_stores.py check` a written step of each release, with no scheduled workflow, which would use paid Actions minutes.

> 1. approve 1.0.0
> 2. Yes we should do do this . I want to know how to do this as well
> 3. Aligned on #455
