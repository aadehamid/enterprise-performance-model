# Enterprise Performance Project Onboarding Guide
**Artifact:** EPM-PROJ-003_Project_Onboarding_Guide  
**Version:** 1.0 Draft  
**Status:** Working Baseline  
**Updated:** August 4, 2026  

*How to establish the project and preserve the work completed so far*

## Recommended approach
Create or use a dedicated ChatGPT Project named:

**Enterprise Performance Model**

Upload the canonical Markdown and HTML artifacts. Use Markdown as the machine-readable and editable source. Use HTML as the human-friendly reading edition.

## Files to upload first
Upload in this order:

1. EPM-FOUND-000 — Master Index
2. EPM-FOUND-000A — Architectural Principles
3. EPM-FOUND-001 — Business Architecture
4. EPM-FOUND-002 — Performance and Data Architecture
5. EPM-FOUND-003 — Semantic Model
6. EPM-FOUND-005 — Measurement and KPI Model
7. EPM-FOUND-006 — Data Product and Consumption Model
8. EPM-FOUND-004 — Ontology Design
9. EPM-PROJ-002 — Project Operating Model
10. Relevant KPI Store technical designs, domain artifacts, Tableau extracts, and migration evidence

## Project setup steps
1. Create the dedicated project.
2. Paste the concise instructions from EPM-PROJ-001 into Project Instructions.
3. Upload all canonical Markdown files.
4. Upload the HTML bundle for easy reading.
5. Create the focused chats listed in the operating model as needed.
6. Start with the onboarding prompt below.
7. Ask the project to confirm the artifact inventory, identify inconsistencies, and use the foundation as the working baseline.

## Copy-ready onboarding prompt
```text
This project contains the canonical Enterprise Performance Model foundation.

Please review the uploaded EPM-FOUND and EPM-PROJ artifacts and treat them as the working baseline unless a later approved artifact supersedes them.

First:
1. Summarize the architecture in your own words.
2. Identify any contradictions, gaps, or unresolved terms across the artifacts.
3. Build an artifact inventory showing ID, title, version, status, purpose, and dependencies.
4. Recommend the next three work packages, prioritizing KPI Store implementation, Tableau measurement classification, Commercial business architecture, and the Netback pilot.
5. Do not silently change accepted definitions. Clearly label recommendations and open questions.
```

## How to bring scheduled briefs into the project
Scheduled briefings can remain in the automation chat.

When a briefing contains a development relevant to the EPM:

1. Copy the relevant briefing or insight into the appropriate project chat.
2. State the purpose of bringing it into the project.
3. Ask whether it changes:
   - a business assumption;
   - causal relationship;
   - KPI requirement;
   - data-product requirement;
   - scenario model;
   - automation opportunity;
   - or L&D requirement.
4. Update canonical artifacts only when the insight results in an accepted design or governance change.

The project should not accumulate all news. It should retain only durable architectural implications.

## How to migrate prior conversations
Do not copy every historical message.

Instead:

- upload the canonical artifacts created from those discussions;
- create short decision summaries for major unresolved topics;
- attach relevant technical designs;
- migrate only important source evidence that is not already captured;
- keep the old chats as historical references.

The objective is to migrate decisions and knowledge, not conversational volume.

## Validation checklist after setup
Confirm that the project can answer:

- What is the difference between a value stream and a capability?
- What is the difference between a measurement, metric, and KPI?
- What is the KPI Store boundary?
- What is the semantic model?
- How does the ontology relate to the semantic model?
- How do foundational and derived data products align with medallion layers?
- Where should reusable logic be implemented?
- How should Tableau calculations be classified?
- What is the first pilot?
- Which artifacts are authoritative?
