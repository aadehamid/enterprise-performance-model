<!-- The decision owner's words, verbatim from urn:epm:issue:205:comment:6116668059 (fetched 2026-10-12). Claude's one-line attribution heading is removed; the rest is verbatim. Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

Please record the following as my source-author responses for Batch 2. These are adopted reference-model positions informed by the downstream business context and industry practice, not verified MPC internal procedures.

For each b-row, add the stated source clarification, mark the source-author question answered, and route the relationship to the scoped-sequence work in #226. Do not emit it as whole-process core:precedes or leave it awaiting another source-author answer. For the c-row, record the final “no sequence” disposition and mark the question done.

1: b — “For a given forecast cycle and version, Publish Forecast and Generate Component Level Forecast Plan (CM-1-1-1-1-4) publishes and makes the approved forecast available before Regional Optimization (CM-1-1-2) uses that version as an approved planning input. Other optimization work may proceed independently; subsequent forecast revisions can prompt another optimization run.”

2: b — “For a given planning cycle, Produce Demand Forecast (CM-1-1-1-1) completes approval and release of the demand-forecast version before Regional Optimization (CM-1-1-2) uses that version as an approved planning input. Forecasting and optimization remain iterative across versions and cycles.”

Questions 1 and 2 describe the same forecast handoff at different hierarchy levels. Preserve that distinction; do not count them as two separate operational handoffs.

3: b — “For each replenishment requirement or approved revision, Manage Inventory Replenishment (CM-1-1-3-7-9) establishes and releases the required product, quantity, destination, and timing before Physical Distribution Scheduling (CM-1-1-3-6) schedules the corresponding movement. Scheduling constraints may feed back into a revised replenishment requirement.”

4: b — “For each plan-selection decision that uses scenario analysis, Perform Scenario Analysis (CM-1-1-4-7-8) provides the relevant evaluated alternatives before the corresponding production plan is selected and approved within Refinery Planning and Optimization (CM-1-1-4). This is an internal step-level sequence, not a sequence preceding the start of the parent process.”

Do not create a new target identity by inference. Preserve the parent relationship’s context and record the plan-selection/approval endpoint for scoped modeling under #226.

5: c — No mandatory sequence. “Forecast Renewables (CM-1-2-1-1-3) estimates future renewable-product or environmental-instrument positions. Perform RINs/REC Actualization (CM-1-2-3-1-7) records applicable actual instrument events independently of forecast completion. Actuals may be compared with forecasts, but that comparison does not establish a forecast-before-actualization prerequisite.”

Keep REL-00149 not emitted with “no sequence—forecast completion is not a prerequisite for recording actual instrument events” as the reason. Do not add a forecast-to-actualization handoff.

6: b — “For each customer quote or renewal version whose composition is owned by Develop Quote (CM-1-3-6-2-4), that version is developed and receives the required authorization before Issue Quotes & Renewals (CM-1-3-7-2-2) issues it to the customer. Preparatory issuance activities may proceed in parallel; revised versions repeat the applicable development and authorization steps.”

7: b — “For each scheduling horizon, Refinery Planning and Optimization (CM-1-1-4) makes the applicable approved plan or authorized revision available before Production Scheduling (CM-1-1-7-2) releases the corresponding executable schedule. Scheduling preparation may overlap planning, and feasibility feedback may trigger plan revisions.”

Complete the source corrections, row-level verdicts, backlog updates, and prescribed validation. All seven source-author questions should count as answered and done for this batch. The six scoped relationships remain pending implementation under #226—not pending further clarification from me.

