# Decision packages, 2026-10-14

Five packages, prepared overnight for the decision owner. *2026-10-18:* The decision owner answered packages 2 to 5 (their words in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-18.md`); *2026-10-19:* they approved package 1 (EPM-DEC-001-0050). The licence and KPI-seed answers are recorded in the pull request that records the answers; the others are carried out in their own pull requests. The licence is recorded in EPM-DEC-001-0041 and the KPI seed in EPM-DEC-001-0040.

When prepared, nothing in them was decided. Each question lists its options with the recommended one first, the reason, and what each answer changes. Reply in the chat with the short form each package gives. The agent then records your words in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/` and makes the changes in pull requests, as usual.

| # | Package | What you answer | Recommended |
|---|---|---|---|
| 1 | [PR reviews of #262, #266, #269](pr-reviews-262-266-269.md) | Accept the three merges, or ask for a follow-up. Change the merge rules so a medium-risk PR waits for you. | Accept all three. Add a GitHub ruleset on `main` that requires the `checks` status and one approving review. |
| 2 | [Step 9 walkthrough](step9-walkthrough.md) | Approve the eleven controlled-value shapes. Choose how canonical facts carry their evidence. | "1a, 2a": approve; one evidence node per fact, keeping the direct triple (a minor `core` release). |
| 3 | [Role questions](role-questions.md) | Seven questions on misspellings, acronyms and competency question 17. | "1 yes, 2 yes, 3 yes, 4 yes, 5 b, 6 table, 7 a". The acronym table needs the expansions only you know. |
| 4 | [Step 7 rulings](step7-rulings.md) | Your Pricing KPI categories; the Market Data and Commercial Risk draft (MD1 to MD5); the MPC proposals P01, P03 to P09 and the rest of P02. | "KPI: list below. MD: all A. P: all A". The KPI list is information only you have. |
| 5 | [Licence](licence.md) | Whether the ontology needs a new licence now. | No: keep it proprietary, all rights reserved, until you decide to publish. |

Three facts the packages found that you may want first:

- The GitHub repository is public and has no LICENSE file, so anyone can read the ontology even though nothing is hosted (licence package). *2026-10-18:* the repository is now private, at the decision owner's instruction. *2026-10-19:* public again temporarily, for the current goal, so the ruleset in package 1 can be enabled (EPM-DEC-001-0050). *2026-10-19, later:* the goal was reached (PRs #298 to #301 merged), and the repository is private again (EPM-DEC-001-0050).
- On #262, #266 and #269, the Cursor app merged 7 to 10 seconds after the bot's MERGE, before the `checks` workflow finished. CI passed afterwards on each (PR review package).
- The domain split in #266 rests on your answer "Option 2: 1.3 Marketing; 1.1, 1.2 Commercial; 1.4 its own . This makes sesne to me. What do you think?". The PR review package asks you to confirm it was a decision.

Hosting is not in these packages. You decided on 2026-10-14 not to host the namespace, because the domain may change. EPM-DEC-001-0039 records it with your words.
