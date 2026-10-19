# Review of the Codex half: summary

This review covers the 149 answers Codex drafted: 102 in `answers-201.jsonl` and 47 in `answers-209.jsonl`. The decision owner should not approve 14 of them as written. Another 24 stand but need a fix to wording, evidence or confidence. `review-codex-half.jsonl` has one review object per answer, in row order.

## Counts

| Severity | #201 | #209 | Total |
|---|---|---|---|
| none | 71 | 40 | 111 |
| minor | 19 | 5 | 24 |
| major | 12 | 2 | 14 |
| **Total** | 102 | 47 | 149 |

## Major findings

**#201 (target identity)**

- **REL-00121.** The target's own scope says it maintains the campaign transition structure. The source names the production scheduling model as its consumer, which is Create Production Scheduling and Sequencing Plan (CM-1-1-7-2-3). This should go to the decision owner flagged.
- **REL-00138.** The answer retargets from the workbook's Daily Execution Planning (CM-1-1-7-1) to Production Scheduling (CM-1-1-7-2) without a flag. The parallel #203 row REL-01122 makes the same retarget and is flagged. A retarget that moves a boundary must be flagged.
- **REL-00156.** The answer is informs, but the decision owner's backlog note reads "likely output dependency". They set it apart from the sibling REL-00148 ("likely informational input"). The suggested answer is uses-input: CM-1-2-1-1-4 core:dependsOnOutputOf CM-1-2-1-1-6.
- **REL-00164.** The decision owner recorded "target identity REJECTED" for this row. The answer retargets to Manage Existing Contract (CM-1-2-1-2-6) with no source evidence. The resulting fact already exists from REL-00163 (the decision owner's #204 Q4).
- **REL-00253.** The source routes agreed term changes to Manage Trade Modifications (CM-1-2-2-2-3), per the decision owner's #204 Q7 sentence. Settlements uses the corrected trade record, not the dispute output. The source names Settlements only in an exclusion.
- **REL-00285.** The decision owner's rejection note says risk limits "constrain/inform" Trading Strategy Management. The answer is governed-by at high confidence and unflagged. A binding limit is constrained-by under the mapping and the industry brief.
- **REL-00506.** The target is chosen on generic fit. Supply Operations (CM-1-2-6-3) excludes physical terminal operations. The source names "terminal and scheduling owners", not Supply Operations.
- **REL-00924.** The target is chosen on generic fit. The workflow configuration serves orders, quotes and master-data changes as well. Neither definition names Establish Commercial Terms & Contracts.
- **REL-00939.** The answer's own reason calls the handoff to billing "indirect", yet it emits unflagged. The backlog records that this row's earlier approval was superseded because plausibility no longer suffices.
- **REL-00960.** The decision owner recorded "target identity REJECTED" for this target. The answer emits uses-input to it at high confidence with no flag.
- **REL-01142.** The only link is the word "supports", which the drafting guide says is not enablement. Supply Operations excludes the physical terminal work the answer relies on.
- **REL-01195.** The target is chosen on sibling proximity. The source names Offer Definition, Pricing, Channel Design and Channel & Partner Management as its consumers, and Sales & Distribution Channel Strategy (CM-1-3-2-4) is not among them. The reason also cites another drafter's pattern as evidence.

**#209 (verb correction)**

- **REL-00294.** The target's scope takes the economic P&L from Perform End-of-Month (EOM) Process (CM-1-2-2-3-5) under the batch 12 binding. That handoff is already stored (REL-00282, REL-00380). The direct edge bypasses it, and its condition is circular.
- **REL-00857.** The source scope excludes price master data (CM-1-3-7-1), and billing reads prices from master data. The answer's own sentence says so, so the fact names the wrong producer.

## Patterns across many rows

- **Identity in #201 rests on fit between definitions.** Most #201 answers confirm the candidate because its definition fits the source's output. Where one scope note names the other process, that is real evidence. Where neither does, the answer is only a proposal. The decision owner's approval is then what confirms identity, and no answer says so. The decision owner's recorded rationale for these holds was "a plausible semantic fit does not confirm the asserted target". Several such answers claim high confidence (REL-00494, 00914, 00919, 01085, 01093).
- **The decision owner's recorded leanings were sometimes ignored.** Four rows carry their "target identity REJECTED" note or a stated lean that the answer departs from: REL-00156, 00164, 00285 and 00960. In the other direction, REL-00239 and REL-00266 are flagged when the decision owner's own notes already say the source informs the target, so they can be decided.
- **Answers duplicate stored facts without saying so.** REL-00304, 00392, 01006 and 01115 produce facts that are already in `canonical-facts.csv`. REL-00164 does the same after its retarget. These rows should attach as extra evidence on the existing fact. REL-01006 also adds a condition the stored fact lacks.
- **The same handoff appears at two hierarchy levels.** Several pairs store one handoff from both a child and its parent. Examples: REL-00681/00687 with REL-01273/01295; REL-00770 with REL-01213; REL-00914 with REL-01250; REL-01163 with REL-01092; REL-00843 and REL-01277 with the decision owner's #205 batch 2 Q6. The decision owner said in #205 batch 2 that one handoff at two levels must not count as two. They may want a rule on whether the parent-level fact is stored at all.
- **Some reasons cite other drafters as precedent.** Examples: "Claude's #203 REL-00152", "Claude's #206 REL-01256" and "Claude's brand-to-channel advice pattern". These are proposals, not records. The reasons should cite the decision owner's backlog notes or the briefs.
- **Evidence lists are boilerplate.** Every answer cites a top-level section of each brief, plus the mapping document. All citations were in the right domain. None names the subsection that carries the point, such as "Market, credit, and inventory risk".
- **Strategy-to-strategy handoffs are drafted two ways.** REL-01195 is informs. REL-01191 and REL-01108 in `answers-202.jsonl` are uses-input. The decision owner should get one pattern.
- **Many conditions are circular.** For example: "when the target processes a quote version composed by the source". They add nothing. They are raised as findings only where they hide a routing question (REL-00294, REL-00843, REL-00857).

## Consistency checks across the register

- No answer in this half creates a reciprocal dependsOnOutputOf, governedBy or precedes pair with `canonical-facts.csv` or any `answers-*.jsonl` file.
- No answer in this half relates a process to its own parent or ancestor.
- REL-00054 (#209) and REL-00067 (#206) propose the same fact, CM-1-1-3-7-9 core:governedBy CM-1-1-3-7-3. REL-01259 (#201) and REL-01256 (#206) also propose one shared fact. REL-00489 (#201) and REL-00476 (#202) do the same. Each pair merges into one fact with two rows. REL-01259's reason wrongly calls REL-01256 the reverse fact.
- REL-00285 (CM-1-2-1-4 governedBy CM-1-2-2-3-6) overlaps #206 REL-00215 (CM-1-2-1-4 governedBy the parent CM-1-2-2-3). The constrained-by suggestion for REL-00285 avoids storing the same authority twice.

## What I could not check

- I did not open the external sources behind the briefs (APQC, filings, vendor pages). I checked each answer against the brief text only.
- I could not confirm whether customer-sale delivery charges settle through Settlements (CM-1-2-4-1) or customer billing (REL-00494). That is a model question for the decision owner.
- I could not find a separate decision record for the batch 12 binding cited in CM-1-2-4-2-6's scope note (REL-00294). I relied on the scope note and the stored facts.
- The B5 backlog lines are garbled ("( → candidate )"). `rows-201.jsonl` carries complete source and target data for those rows, so they were still reviewable.
