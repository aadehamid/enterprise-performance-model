<!-- The decision owner's words, verbatim from urn:epm:issue:204:comment:6130380041 (fetched 2026-10-12). Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

Please record the following as my source-author responses for issue #204, Batch 1. These are adopted reference-model operating rules informed by industry practice

I agree that a conditional trigger fits the locked core:triggeredBy definition where the condition identifies a specific event, finding, or authorized handoff that invokes the target. No new relation or design round is needed merely because a trigger has a condition.

Preserve the distinction between invoking the target for assessment or processing and automatically approving its eventual business action.

1: b — “When Monitor and Control Inventory Positions (CM-1-1-3-7-12) identifies an actual or projected inventory shortfall against the applicable replenishment threshold, or another inventory exception assessed as requiring corrective resupply, it raises a replenishment referral to Manage Inventory Replenishment (CM-1-1-3-7-9). Upper-limit breaches and other exceptions that do not require resupply do not trigger this handoff.”

2: b — “When Monitor Risk (CM-1-2-2-3-8) identifies a limit breach, or a near-breach meeting the approved escalation criteria, it refers the finding to Manage Risk Limits (CM-1-2-2-3-6) for assessment and an authorized limit-management decision. The referral does not automatically authorize a temporary excess, limit change, or suspension.”

3: b — “When Manage Card Administration (CM-1-3-6-6-4) releases an authorized instruction requiring production of a new, replacement, or reissued card, it invokes Manage Card Production & Monthly Reissue (CM-1-3-6-6-13). Administrative changes that do not require card production do not trigger this handoff.”

4: b — “When Monitor Contracts (CM-1-2-1-2-11) identifies an expiry, renewal window, or obligation finding that requires consideration of an amendment, extension, or renewal, it refers the finding to Manage Existing Contract (CM-1-2-1-2-6) for assessment and the applicable approval process.”

5: b — “When assessment of a corporate event under Manage M&A Activity (CM-1-2-1-2-4) results in an authorized instruction to offboard a counterparty or process a change of counterparty through the applicable transfer or novation procedure, that instruction invokes Terminate/Novate Counterparty (CM-1-2-1-2-3). A corporate event alone does not trigger termination or novation; applicable legal, credit, and consent requirements remain in force.”

6: b — “When assessment of a corporate event under Manage M&A Activity (CM-1-2-1-2-4) results in an authorized instruction to terminate or novate an affected agreement, that instruction invokes Terminate/Novate Contract (CM-1-2-1-2-7). A corporate event alone does not trigger the action; contractual rights, approvals, and required consents remain applicable.”

7: b — “When resolution of a confirmation dispute under Manage Confirm Disputes (CM-1-2-2-2-5) produces an authorized, agreed change to the trade’s commercial terms, it hands the change to Manage Trade Modifications (CM-1-2-2-2-3) for the controlled record update and applicable re-confirmation. A correction that merely restores the record to terms already agreed does not constitute this changed-terms trigger and follows the appropriate correction workflow.”

8: a — “Each potential external trading-compliance violation identified by Monitor External Trading Compliance (CM-1-2-4-3-2) invokes Manage Exceptions (CM-1-2-4-3-7) through a documented exception referral for intake and assessment, either opening a case or updating an existing case. Referral does not mean the violation has been substantiated.”

9: a — “Each internal trading-compliance violation or adverse pattern identified as a compliance concern by Monitor Internal Trading Compliance (CM-1-2-4-3-3) invokes Manage Exceptions (CM-1-2-4-3-7) through a documented exception referral for intake and assessment, either opening a case or updating an existing case.”

10: a — “Each internal trade-control failure or design gap identified by Monitor Internal Trade Controls (CM-1-2-4-3-4) invokes Manage Exceptions (CM-1-2-4-3-7) through a documented exception referral for assessment and tracking of the applicable response, either opening a case or updating an existing case.”

11: a — “Each material tax-compliance gap identified by Manage Tax Compliance (CM-1-2-4-3-5), assessed against the applicable approved materiality and escalation criteria, invokes Manage Exceptions (CM-1-2-4-3-7) through a documented exception referral for assessment and tracking of the applicable response. Required statutory reporting, correction, or payment obligations are not delayed by the internal exception workflow.”

For Questions 8–11, the findings named in each sentence define the trigger events. Routine monitoring results that identify no such finding are not triggers. Question 11’s materiality qualification defines the event; it is not permission to disregard obligations below an internal materiality threshold.

Save this response word for word, append the approved sentences to the relevant source scope notes, re-pin Step 4, and perform the fresh row-level reviews. Record conditions explicitly and emit approved relationships in the direction target core:triggeredBy source, following the existing conditional-trigger pattern.

Mark all 11 source-author questions answered. Complete the prescribed validation, traceability, and review checks, and open the batch PR as “Part of #204.” Close #204 when all 11 fresh verdicts and required updates have landed. Do not report the changes as implemented before the PR merges.
