# Domain Docs

How the engineering skills (`domain-modeling`, `grill-with-docs`, `research`,
`wayfinder`, and others) should read and write this repo's domain
documentation. This repo keeps its glossary and decisions as EPM artifacts
rather than the skills' default `CONTEXT.md` + `docs/adr/`.

## Before exploring, read these

- **Business glossary (EPM-GLOS-001):** `business_architecture/domain/business-glossary.md`.
  The skills' "`CONTEXT.md`" means this file here.
- **Architecture decision records (EPM-DEC-001):** `business_architecture/domain/decisions/`.
  The skills' "`docs/adr/`" means this folder here.
- **Existing decision logs** keep authority for their own scope. Read the one
  that touches your area:
  - `EPM-FOUND-000.md`: master index, decisions table (D-xx), conflicts and open issues
  - The ontology playbook, reached via `business_architecture/ontology/README.md`:
    locked policies in the method copy's §2, and the dated journal in the working record
  - `business_architecture/ontology/step4/step4-decisions.md`: Step 4 design decisions (Q1–Q12)
  - `business_architecture/domain/data-domain-register.md`: data domains and boundary rules
  - `EPM_Homelab/02-Tool-Selection-and-ADRs.md`: homelab ADRs (ADR-HL-xxx)

If the glossary or the decisions folder doesn't exist yet, **proceed
silently**. `/domain-modeling` creates them lazily when the first term or
decision is actually resolved.

## Precedence

- `business_architecture/` takes precedence over other folders.
  `business_architecture/business_process/` and `business_architecture/schema/`
  are the process authority.
- Source precedence follows `README.md` ("Source precedence").
- Don't duplicate a decision that already lives in one of the logs above. Link
  to it instead.

## Writing new entries

- **Glossary entry:** term, definition, "avoid" synonyms, source (cite the
  evidence file or filing), status (Draft / Candidate / Approved Baseline). A
  term says **Approved Baseline** only when Hamid has recorded that approval. A
  PR merge alone doesn't approve it.
- **Decision record:** one file per decision, `EPM-DEC-001-NNNN-<slug>.md`, with
  context, decision, alternatives considered, evidence, status (Proposed /
  Decided / Superseded) and date. A record says **Decided** only when Hamid has
  recorded the decision. A PR merge alone doesn't decide it.
- Every change lands through a PR (see `AGENTS.md`).

## Use the glossary's vocabulary

When output names a domain concept (issue title, proposal, test name), use the
term as defined in the business glossary, or in the domain register and
evidence files until the glossary exists. Don't drift to synonyms. A missing
term is a signal: either the language is invented (reconsider), or there's a
real gap (note it for `/domain-modeling`).

## Flag decision conflicts

If output contradicts an existing decision, say so explicitly rather than
overriding it silently:

> _Contradicts EPM-DEC-001-NNNN (<decision title>), but worth reopening because…_

(Placeholder format only. No EPM-DEC-001 record exists yet.)
