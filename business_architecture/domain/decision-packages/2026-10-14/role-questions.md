# Role questions from the role register

*2026-10-18:* answered by Hamid (`answers-2026-10-18.md`); carried out by organization 2.0.0 (EPM-DEC-001-0045).

Prepared for Hamid on 2026-10-14. This package decides nothing. It sets out the questions EPM-DEC-001-0031 leaves for you (lines 31 to 39), with the evidence for each answer, and says how they relate to competency question 17.

The register maps the 91 role strings in the process map's RACI lists to 60 roles: 54 positions and 6 teams (`business_architecture/ontology/organization/build_roles.py`, run at commit `6baf510`). Its rule 1 merges two strings only when they differ in case, plural, punctuation or "&" against "and" (EPM-DEC-001-0031, line 22). Every question below asks for a merge or a definition that rule 1 does not allow on spelling alone. Occurrence counts come from reading the `raci` lists of `business_architecture/business_process/downstream_process_map.json` with `build_roles.py`'s own reader. "R", "A", "C" and "I" are the four RACI levels.

## What you need to do

Reply with one word per line, for example "1 yes, 2 yes, 3 yes, 4 yes, 5 b, 6 table, 7 a".

1. Are "RCVO Advisor" and "RVCO Advisor" one role? Recommended: yes, "RCVO" is a typo.
2. Is "Forecaster" the Local Refinery Forecaster? Recommended: yes.
3. Is "Refinery Technical Service Representative" the Refinery Technical Representative? Recommended: yes.
4. Are the two VP strings that differ only in "RVCO" one VP? Recommended: yes.
5. What is "Crude RFC"? Recommended: b, RFC means Refinery Feedstock Coordinator, and Crude RFC stays its own role.
6. What do the acronyms stand for? Recommended: give the expansions you know, using the table in question 6. I record only what you confirm.
7. How should competency question 17 be handled? Recommended: a, as a separate decision. The role answers do not unblock it.

## How answers become changes

The organization module 1.0.0 is already released with these roles. For example, `role:rcvo-advisor` is in `business_architecture/ontology/releases/organization/1.0.0/organization.ttl` (line 6662). A merge cannot delete a role. The playbook says to deprecate it and point it at its successor, and to do that only in a major release (`business_architecture/ontology/ontology-playbook.md`, Appendix B, sections "What counts as what" and "Deprecation (never delete)"). Any "yes" to questions 1 to 4 therefore needs organization 2.0.0, and majors need your approval (EPM-DEC-001-0037, line 12). I suggest one major release that carries every merge you confirm. An expansion in question 6 adds a definition to a role. That is an addition or a clarification, so a minor or patch release is enough, and the module owner can issue it. Each answer also updates `roles.csv`, `role-register.csv` and EPM-DEC-001-0031 in a PR (0031, line 59).

## Question 1. RCVO Advisor and RVCO Advisor

| Source string | Entries | Where |
|---|---|---|
| RCVO Advisor | 1 | CM 1.1.2.8.1 (R) |
| RVCO Advisor | 32, on 32 processes | Under CM 1.1.2 Regional Optimization and CM 1.1.4.4: R on 3, C on 4, I on 25 |

Today the register keeps two roles, `rcvo-advisor` and `rvco-advisor`. One assignment points at the first.

Proposed answer: yes, one role, and "RCVO" is a typo. The evidence is strong. CM 1.1.2.8.1, the one process that writes "RCVO Advisor" in its RACI, writes "RVCO Advisor" among its SIPOC customers. The string "RCVO" appears once in the whole process map, while "RVCO" appears 49 times, including in the role "VP RVCO".

- Yes. `rcvo-advisor` is deprecated in favour of `rvco-advisor`, and its one assignment moves. The register goes from 60 roles to 59.
- No. The two roles stay apart, and "RCVO" needs its own expansion in question 6.

## Question 2. Forecaster

| Source string | Entries | Where |
|---|---|---|
| Refinery technical representative/Forecaster/ E&P manager | 1 | CM 1.1.5.5 (C) |
| Refinery technical service representatives/Forecasters/ E&P manager | 1 | CM 1.1.5.5.3 (C) |
| Local Refinery Forecaster | 1 | CM 1.1.5.6.9 (C) |
| Local Refinery Forecaster (Prompt) | 2 | CM 1.1.5.6.1 and CM 1.1.5.6.8 (C) |

Today the register splits each compound string into its roles (rule 3) and keeps "Forecaster" as a role of its own (`business_architecture/ontology/organization/roles.csv`, `forecaster`).

Proposed answer: yes, Forecaster is the Local Refinery Forecaster. The evidence is moderate. All five entries are Consulted on case runs under CM 1.1.5 Regional Backcasting. On CM 1.1.5.6.1 and CM 1.1.5.6.8, the Local Refinery Forecaster (Prompt) is consulted together with the E&P Manager, the same pairing as in the two compound strings. No string says "local refinery" next to the bare "Forecaster", so this is an inference.

- Yes. `forecaster` is deprecated in favour of `local-refinery-forecaster`, and its 2 assignments move.
- No. Forecaster stays a separate role, and it needs a definition from you.

## Question 3. Refinery Technical Service Representative

| Source string | Entries | Where |
|---|---|---|
| Refinery technical service representatives/Forecasters/ E&P manager | 1 | CM 1.1.5.5.3 (C) |
| Refinery technical representative/Forecaster/ E&P manager | 1 | CM 1.1.5.5 (C) |
| Refinery technical representative | 5 | CM 1.1.5.1, CM 1.1.5.1.2, CM 1.1.5.1.2.3, CM 1.1.5.7, CM 1.1.5.7.5 (C) |

Today the register keeps `refinery-technical-service-representative` apart from `refinery-technical-representative`.

Proposed answer: yes, one role. The evidence is strong. CM 1.1.5.5.3 is a child of CM 1.1.5.5. The two compound strings name the same three parties in the same order, and only the child adds "service" and plurals.

- Yes. The first role is deprecated in favour of the second, and its 1 assignment moves.
- No. Both roles stay, and the service representative needs a definition.

## Question 4. The two VP strings

| Source string | Entries | Where |
|---|---|---|
| VP (Clean Products, Crude Trading, NGLs, Asphalt, Petchem) | 1 | CM 1.1.2.8.2 (I) |
| VP (Clean Products, RVCO, Crude Trading, NGLs, Asphalt, Petchem) | 2 | CM 1.1.2.8 and CM 1.1.2.8.4 (I) |

Today the register keeps two VP roles.

Proposed answer: yes, one VP. The evidence is moderate. On CM 1.1.2.8.2, the RACI Informed list starts with the VP without "RVCO", and the SIPOC customer list starts with the VP with "RVCO". Supply Operations Director, Regional Business Director, Crude Planning and Optimization Director and BP&A appear in both lists.

A third string, "VP RVCO", is not part of this question. It is Accountable on CM 1.1.2.8 and CM 1.1.2.8.2, where the long VP is Informed, so it names a different party.

- Yes. The VP without "RVCO" is deprecated in favour of the VP with it, and its 1 assignment moves.
- No. Both VPs stay.

## Question 5. Crude RFC

| Source string | Entries | Where |
|---|---|---|
| Crude RFC | 2 | CM 1.1.5.6.2 Build and run actual global crude purchase case, CM 1.1.5.6.3 Build and run actual crude allocation case (C) |
| Refinery Feedstock Coordinator | 13 | Under CM 1.1.2 and CM 1.1.5.1 (R on 2, C on 11) |

Outside the RACI lists, "Crude RFC" is a SIPOC customer of CM 1.1.2.5.1, CM 1.1.2.5.2, CM 1.1.2.5.5 and CM 1.1.2.5.9. "RFC" alone is a SIPOC supplier of CM 1.1.5.5.1, a feed optimization case that covers "crude + feedstock optimization". The system "RFC Hindsight Analysis Excel" supports CM 1.1.5.1, CM 1.1.5.1.2 and CM 1.1.5.1.2.1, where the Refinery Feedstock Coordinator is Consulted. Today the register keeps `crude-rfc` as its own role (`roles.csv`).

Proposed answer: b. The evidence that RFC means Refinery Feedstock Coordinator is moderate. Whether "Crude RFC" is the same position is weaker. The register already keeps Crude Oil Trader apart from Trader because the source names the commodity (`roles.csv`, `crude-oil-trader`). The register also has a separate Crude Coordinator, consulted on CM 1.1.5.1 next to the Refinery Feedstock Coordinator.

- a. Crude RFC is the Refinery Feedstock Coordinator, with "crude" as a qualifier. `crude-rfc` is deprecated in favour of `refinery-feedstock-coordinator`, and the 2 assignments keep "Crude" in their source text.
- b (Recommended). RFC means Refinery Feedstock Coordinator, and Crude RFC stays its own role, with the definition "Refinery Feedstock Coordinator for crude". This adds a definition and needs no major release. EPM-DEC-001-0031 notes that splitting later costs more than merging later (line 43).
- c. RFC means something else. You give the expansion.

## Question 6. The acronyms

EPM-DEC-001-0031 found no expansion in the repository and no MPC or peer filing in `business_architecture/reference/` that names these roles (lines 16 and 53). I searched the process map's other fields for clues. The candidates below are guesses unless you confirm them. Each confirmed expansion becomes a role definition.

| Acronym | Role strings and entries | Clue in the process map | Candidate |
|---|---|---|---|
| CP | CP Manager: 4 (I on CM 1.1.5.4.2, CM 1.1.5.5.8, CM 1.1.5.6.10; C on CM 1.1.5.9.3) | CM 1.1.2.2.2 gathers deals "for Clean Products" from the supplier "CP Trader". The Global Feedstocks Manager has the same 4 entries as the CP Manager. | Clean Products |
| CPVC | CPVC schedulers: 3 (C on CM 1.1.5.5, CM 1.1.5.5.6, CM 1.1.5.5.7) | "CPVC SVP" and "CPVC VPs" are customers of CM 1.1.5.8.5. CM 1.1.5.8.4 says "South: GFVC and CPVC". | Starts with Clean Products. "VC" is not explained anywhere. |
| GFVC | Manager: GFVC: 10, on 7 processes (C and I under CM 1.1.5.8) | Paired with CPVC as above. "GFVC SVP" and "GFVC VPs" are customers of CM 1.1.5.8.5. | Starts with Global Feedstocks, by the CP pairing. "VC" is not explained. |
| RVCO | RVCO Advisor: 32; VP RVCO: 2; the long VP: 2 | Ends in the same "VC" plus "O" as CPVC and GFVC. | None |
| CCI | CCI Director: 108, on 55 processes (A and I across CM 1.1.5 and CM 1.1.6, and C once on CM 1.1.5.9.3) | "CCI Group" is a customer. CM 1.1.5.8.5 presents outcomes "in CCI Management Review meeting". | None |
| E&P | E&P Manager: 2, plus 2 inside compound strings; E&P Supervisor: 4 (A on CM 1.1.4.1.1 to CM 1.1.4.1.4) | E&P Supervisor is accountable for the refinery premise. The register also has a "Refinery Econ & Planning Supervisor" (10 entries under CM 1.1.5.8). | Economics & Planning. In a refinery it is unlikely to mean Exploration & Production, an upstream term. If you confirm, E&P Supervisor may be the Refinery Econ & Planning Supervisor, a further merge to ask about. |
| PSM | PSM: 2 (C on CM 1.1.4.1.1 and CM 1.1.4.1.2) | None | Possibly Process Safety Management: 29 CFR 1910.119 is titled "Process safety management of highly hazardous chemicals" (eCFR, read 2026-10-14). The map gives no support. |
| BP&A | BP&A: 3 (I on CM 1.1.2.8, CM 1.1.2.8.2, CM 1.1.2.8.4) | Also a SIPOC supplier of CM 1.1.5.1 and four of its sub-processes, once as "BP&A (Export Sales Price)". | None |
| RO | Business Analyst (RO): 1 (C on CM 1.1.5.1.1) | CM 1.1.4.2 is named "Receive RO Targets", and its description says the targets come from the "Regional Plan Output". CM 1.1.2 is named "Regional Optimization". | Regional Optimization |

RCVO is covered by question 1 and RFC by question 5.

Options:

- a (Recommended). Give the expansions you know, and name who can answer the rest. I record only what you confirm, as role definitions in a minor or patch release.
- b. Confirm the candidates in the table as they stand. I record them as definitions.
- c. Leave them undefined for now. The roles keep a label and no definition, which `business_architecture/ontology/organization/shapes.ttl` allows until the register supplies definitions (EPM-DEC-001-0030).

## Question 7. Competency question 17

Q17 asks "Who owns the meaning of a concept, and who only stewards the data?" (`business_architecture/ontology/competency-questions.md`, line 54). `business_architecture/ontology/regression/expected.csv` marks it as waiting for Step 5 (line 18).

The role answers do not unblock Q17. Questions 1 to 6 change the names and definitions of roles that hold RACI assignments on processes. Q17 needs two things those answers do not supply:

- A relation from a concept to the role that owns its meaning, kept apart from RACI. EPM-DEC-001-0030 left "the relation for who owns a meaning" to a later slice (line 33). RACI binds a role to a process at design time (`business_architecture/ontology/ontology-playbook.md`, Step 5, lines 406 to 408). It does not say who owns what a concept means.
- The data itself, meaning who owns each concept's meaning. No source in the repo gives this per concept.

The register does hold an IT Data Owner (A on 8 processes under CM 1.1.2.1 Model and System Maintenance and CM 1.1.2.2), an IT Data Steward (I on 8) and an IT Data Custodian (C on 1). These are RACI parties on processes. They could fill the "steward" side of Q17 later, but they do not answer it now.

- a (Recommended). Handle Q17 as a separate decision. I draft a short package with the relation, its shape and where the owner data would come from. Q17 stays "waits" until you decide.
- b. Park Q17 by a recorded decision. EPM-DEC-001-0019 counts a parked question as green, and the regression suite would stop listing it as waiting.
- c. Treat the IT Data Owner and IT Data Steward assignments as the answer. Not recommended: they cover 8 processes, not the meaning of concepts.
