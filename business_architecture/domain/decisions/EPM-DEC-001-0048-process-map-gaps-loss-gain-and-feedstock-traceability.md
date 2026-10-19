# EPM-DEC-001-0048: the two process-map gaps are filled from MPC's public information first

| Field | Value |
|---|---|
| Status | Decided (Hamid, 2026-10-19: fill both gaps from high-quality references, MPC's public information first; what is added delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | The two gaps the MPC-P03 and MPC-P04 checks found (`business_architecture/business_process/proposals/MPC-P03-transfer-coverage-gaps.md`, question 1; `MPC-P04-renewables-traceability.md`) |
| Source | Claude Code session, 2026-10-19 |

## Context

Under EPM-DEC-001-0047, the checks Hamid set on MPC-P03 and MPC-P04 found two gaps, and the pull requests proposed them to him instead of adding processes. First, no step names the loss and gain reconciliation of a movement, although the Loss Control data product exists. Second, no step keeps the traceability and carbon-intensity evidence that renewable feedstock credits depend on.

## Decision

**Hamid's decision:** address both gaps from high-quality reference material, with MPC's public information taking precedence over any other source.

**What follows (Claude, under EPM-DEC-001-0028):**
1. **Loss and gain.** One step, CM 1.1.3.7.13 Reconcile Movement Losses and Gains, under CM 1.1.3.7 Inventory, covering every movement, not only inter-refinery transfers. MPLX's FY2025 10-K describes the work: volume gains and losses from "pressure and temperature changes, evaporation and variances in meter readings and other measurement methods", and imbalances "settled in cash, settled by physical delivery of volumes from a different source, or tracked and settled in the future" (`reference/mpc/loss-gain-and-feedstock-evidence.md`, LG-01). API MPMS Chapters 17.5 and 23 support the reconciliation method (support only). This is option A of the MPC-P03 proposal, question 1. It produces the Loss Control data product. Question 2 of that proposal (quality of transferred intermediates) is not part of Hamid's answer and stays open.
2. **Feedstock traceability.** One step, CM 1.2.5.1.5 Manage Renewable Feedstock Traceability and Carbon-Intensity Evidence, under CM 1.2.5.1 Crude/Feed Quality Management, feeding environmental credit and clean-fuel incentive management (CM 1.2.4.3.8). MPC's own disclosures describe the work: its feedstock suppliers adhere to "a supplier feedstock information compliance commitment" that includes "renewable biomass certifications, source locations" (CDP 2023), and MPC was "developing a sustainability due diligence process to assess risk within our renewable feedstock supply chain" (2022 Sustainability Report) (FT-01, FT-02). The regulators' record rules then set what the step keeps: EPA RFS (40 CFR 80.1454(b)(3)(vi) and (j)), CARB LCFS (section 95488.9(g)) and the IRS proposed 45Z rules (proposed section 1.45Z-4(f)(1) and (g)(1)) (`reference/downstream-peers/loss-gain-and-feedstock-regulatory-evidence.md`). ISCC EU 203 supports the chain-of-custody method (support only). This is option A of the MPC-P04 proposal.
3. Each step follows the map's conventions (ID, level, name, description, `renewablesSpecific` where it applies), and the curated identity map gets its row as Step 2 would emit it.

## Alternatives considered

- **Widen existing descriptions instead (option B of each proposal).** Not chosen: each gap is a separate control with its own outputs (the Loss Control data product; the eligibility records the credit processes consume), and MPC's and MPLX's disclosures describe each as work in its own right.
- **Leave the gaps open (option C).** Not chosen: Hamid said to address them.

## Hamid's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/answers-2026-10-19-morning.md`: "On two gaps the process-maps found. Address it using high quality refrence materials. Any publickly available informtion from Marathon superseded any other information". Items 1 to 3 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and Hamid can reverse them.

## Evidence

`business_architecture/reference/mpc/loss-gain-and-feedstock-evidence.md` (MPC and MPLX, first); `business_architecture/reference/downstream-peers/loss-gain-and-feedstock-regulatory-evidence.md` (regulators, then industry standards as support); the two proposals named above; EPM-DEC-001-0047.

## Consequences

- The two proposals record the gaps as filled, and their rows in `process-map-suggestions.md` say so.
- The Loss Control data product names the process that produces it.
