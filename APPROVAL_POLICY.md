# Approval policy — Bugbot is optional

This repo's PR Routing & Approval agent (`Pr approval agent`) must review every PR from the diff. It must not treat Bugbot as a required gate.

## Bugbot skip is not a stop

If Bugbot does not complete, is skipped, hits a usage/spend limit, or posts "couldn't run" / no findings:

- Do **not** stop.
- Do **not** refuse to review.
- Do **not** withhold your own risk assessment because Bugbot is missing.
- Review the PR yourself from the diff, commit messages, and PR body.

A missing Bugbot signal is absence of evidence, not a finding. Do not invent Bugbot findings. Do not wait for credits to be added.

## What to do instead

1. Read the diff and classify risk yourself.
2. Leave a review comment with that assessment (what you checked, residual risk).
3. Request reviewers only when the risk or domain actually needs a human — not because Bugbot failed.
4. Approve only if the change is otherwise eligible under risk threshold and any more-specific policy. Do not approve solely because Bugbot is missing, and do not refuse solely because Bugbot is missing.

## Still require a human when

- The PR is a Step 3c definition batch (workbook approvals) unless Hamid has already recorded the decisions in the PR body and the mechanical gate is `blocking=0`.
- The PR changes approval policy, routing, or this file (use the base-branch version; do not relax review on the same PR).
- Risk is medium or higher on your own reading of the diff.
