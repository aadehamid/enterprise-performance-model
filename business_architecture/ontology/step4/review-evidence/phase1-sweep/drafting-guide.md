# Phase 1 sweep: drafting guide

This guide is for the agents drafting answers to the held Phase 1 rows, and for the agents reviewing those drafts. The decision owner delegated the drafting ("research … then take the best of both worlds to inform how you will handle the ontology", session of 2026-10-12; proposal on #207). They approve the finished register before anything is built. An answer drafted here is a **proposal**, never a decision.

## Inputs, all in this folder

- `rows-<issue>.jsonl`: one row per line. Each has the verb, source, candidate target(s), disposition, hold set, backlog note, and the source's and every target's label, definition, scope note and parent.
- `research-mpc.md`: MPC's public evidence, with citations.
- `research-industry.md`: peers and industry practice, with citations, written by Codex.
- **The authoritative rules**, in the repo at `~/Dropbox/1_PROJECTS/Enterprise Performance Model`, read-only:
  - `business_architecture/ontology/step4/verb-predicate-mapping-v2.md`: predicate meanings, canonical directions, the triggers rule (the "Triggers" section), the no-two-cycle rule, and the G1/G2/G3 enables groups.
  - `business_architecture/ontology/step4/evidence-discipline.md`: the evidence rules, affirmative citation, and the nearness-only identity rule.
  - `business_architecture/ontology/step4/source-workbook-backlog.md`: each issue's section explains why its rows are held.
  - The decision owner's own answers, as precedent for tone and evidence basis: `step4/review-evidence/decision-owner-answers/204-batch1.md`, `205-batch1.md`, `205-batch2.md`.

## Rules every answer follows

1. **Answer the question the row is held for.**
   - #201: name the intended target. A candidate picked by label similarity or nearness is not evidence.
   - #202 and #209: is the verb right?
   - #203: enables or informs?
   - #206: what is the authority?
   - #210: each row's own hold reason.
2. **Use the locked meanings.**
   - **enables:** the target cannot operate as defined without a capability or condition the source provides.
   - **informs:** the source's analysis, recommendation or plan is an input the target considers while keeping its own decision.
   - **uses-input / dependsOnOutputOf:** one process consumes a named output of another. The stored fact is always `consumer core:dependsOnOutputOf producer`.
   - **governed-by:** one process operates within policy, authority or limits that another owns. The stored fact is always `governed core:governedBy owner`.
   - **triggers:** a defined event, finding or handoff from the source starts the target.

   **Correction, 2026-10-12.** An earlier version of this guide gave uses-input and governed-by in the wrong direction. The mapping document's canonical direction table is the authority: `uses-input (S, T)` is stored as `S core:dependsOnOutputOf T`, and `governed-by (S, T)` as `S core:governedBy T`. Every answer was checked: each stored fact is right in meaning, and the `direction` field records whether the fact keeps the row's own direction (`as-asserted`) or reverses it (`reversed`). Judge each answer by its `stored_fact` and sentence, not by the verb label alone.

   "Feeds", "supports" and "is associated with" are not enablement. A statement of where work happens is not a citation.
3. **No hierarchy restatements.** A child relating to its own parent or ancestor only restates the taxonomy. Answer "no relationship" unless the child produces something specific the parent uses beyond being part of it, and then say what.
4. **Every emitting answer needs a scope-note sentence.** It goes in the **source** process's scope note, names both processes with their slugs, for example "Monitor Risk (CM-1-2-2-3-8)", and states the relationship in plain words. If the relationship holds only under a condition, the sentence states the condition, as the decision owner's #204 answers did.
5. **Evidence basis on every row.**
   - **mpc-sourced:** the research brief cites MPC for the relationship itself, which is rare.
   - **reference-model:** MPC evidence supports only the context, and the handoff follows industry practice. Most rows will be this.

   Cite the brief section or source you relied on.
6. **Do not invent identity.** Never create a new process, and never retarget to a process that is not in the taxonomy. A retarget must name an existing slug with its label.
7. **Flag instead of guessing.** Set `confidence: low` and `flag: true` when:
   - the evidence doesn't decide between two answers;
   - the answer would change the model's structure, such as a new process, a moved boundary or an ownership change;
   - the row's target data is missing or garbled;
   - or the right answer contradicts one of the decision owner's recorded positions.

   Flagged rows go to the decision owner; they are not decided here.

## Output: one JSON object per row, in `answers-<issue>.jsonl`

```json
{"row_id": "REL-00000", "issue": 201,
 "verdict": "confirm | correct-verb | retarget | no-relationship",
 "verb": "the verb after the answer (enables, informs, uses-input, governed-by, triggers, requires, constrained-by, assures, precedes); empty for no-relationship",
 "target_slug": "the target after the answer; for retarget, the new slug",
 "stored_fact": "e.g. CM-1-2-2-3-6 core:informedBy CM-1-2-2-3-12; empty for no-relationship",
 "condition": "empty, or the condition, which the sentence also states",
 "scope_note_sentence": "the sentence for the source's scope note; empty for no-relationship",
 "reason": "two or three plain sentences on why, citing the evidence",
 "evidence_basis": "mpc-sourced | reference-model",
 "evidence": ["research-mpc.md §2", "research-industry.md §…", "target scope note"],
 "confidence": "high | medium | low",
 "flag": false,
 "flag_reason": "",
 "source_slug": "the row's source", "direction": "as-asserted | reversed; empty for no-relationship"}
```

**Done when** every row in your issues has exactly one object, every emitting answer has a sentence naming both slugs, and every low-confidence row has `flag: true` with a reason.
