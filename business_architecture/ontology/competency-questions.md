# Competency Questions — Baseline

**Status:** Draft under review (2026-09-18).
**Purpose:** the acceptance test for the ontology. If the model cannot
answer a question here, the model is incomplete — not the question.
These double as the Step 11 SPARQL regression tests.

**Sources merged:** the process-map question set (Kailey, 2026-09-17)
and Hamid's domain question set A–F (2026-09-18), minus the constraints
section (parked 2026-09-18 — constraints are not being modeled). Light
editorial merges are marked; Hamid's wording is otherwise preserved
verbatim.

---

## I. Process structure & navigation
1. What are the child processes of X, and what is the full root-to-leaf
   path of process P?
2. Which processes are orphans — no parent, or no children where children
   are expected?

## II. Responsibility (RACI)
3. Who is Accountable / Responsible / Consulted / Informed for process P?
4. Which processes have no accountable owner?
5. Which roles participate in process P?

## III. Systems & data products
6. Which systems (XPIMS, DPO, RightAngle, …) support process P, and which
   processes depend on system S?
7. What data products does process P produce or consume? Which data
   products have no owning process? (cf. Loss Control)
8. Which processes have empty `produces` / `consumes`?

## IV. Lanes, capabilities, value streams
9. Which processes sit in each office lane, and which lanes are thin?
10. Which processes realize capability C or participate in value stream V?

## V. APQC alignment
11. Which local processes reference APQC element E, and which APQC
    elements have no local counterpart?
12. Where did we deliberately diverge from APQC, and why? (boundary
    notes)

---

## VI. Shared meaning — what kind of thing is this?
13. What is a concept vs a named measure vs a report?
14. Which concepts are allowed to become a number, and which must never
    become one?
15. If two teams use the same English word, how do we tell whether they
    mean the same thing?
16. What is the official name, what are the aliases, and what is
    explicitly out?
17. Who owns the meaning of a concept, and who only stewards the data?
18. When a definition changes, what stays the same (the identity) and
    what gets a new version?
- *Done when:* "Customer" cannot be classified as a KPI, and
  "3-2-1 Crack Spread" can.

## VII. Customer / Party — first domain module
19. What is a Party, and how is it different from a Customer Account?
20. Which roles can the same Party hold at the same time (Sold-to,
    Bill-to, Payer, …)?
21. Are those roles permanent types, or time-bounded holds? Is Ship-to a
    role or a location?
22. What is a Loading-Authorized Party, and how is that different from an
    Authorization object?
23. Where does credit sit — on the Party, the account, or the Payer?
24. Can the same organisation be a customer in one deal and a supplier /
    exchange counterparty in another? How is that modeled without a
    second "Customer" class?
25. Which concept should a customer-grained KPI bind to — Party, Account,
    Sold-to, Payer, or site — and why not the bare word "Customer"?
26. What questions about "who is the customer on this order?" must resolve
    to one role, not a blob?
- *Done when:* five real multi-role organisations can be described both
  ways (Party→roles and role→Party) without calling Customer a role.

## VIII. Named KPI — the bind to the Store
*The ontology answers what a Named KPI is. It does not calculate it.*
27. What is a Named KPI, as a concept, before anyone computes it?
28. What population is in the Named KPI, and what is out (in business
    words)?
29. What grain is the thing we named (day × series × tenor vs a monthly
    roll-up)?
30. Is a monthly average a second Named KPI, or a way of asking for the
    same one?
31. When are two published series the same Named KPI vs two different
    ones (region, ratio, ex-RIN vs inc-RIN, blended vs regional)?
32. What is 3-2-1 Crack Spread *not* (realized refinery margin, capture,
    $MM R&M, a homemade 3-2-1 from product and crude legs)?
33. Which process, decision, or capability does this Named KPI inform?
    What decisions does it support?
34. Which domain concepts does it quantify (region, product slate, crude
    marker) — without putting the formula in the ontology?
35. How does a catalog row point at this Named KPI, and what must already
    exist before that pointer is filled?
36. If an assistant asks for "the crack," which Named KPI is the official
    one, and which nearby series are related but not it?
- *Done when:* Crack Spread has a published identity the catalog can
  bind, and "Customer" still has none.
- *(Editorial: Q33 merges the former section-D question "What decisions
  does this Named KPI support?")*

## IX. Process placement — where the work sits
37. What process (or capability) does a concept or Named KPI sit on?
38. Is that placement certification, or only context? *(If two processes
    use the same name, are they the same meaning — or the same label on
    different meanings?)*
39. What breaks upstream or downstream if the meaning changes?

## X. Publication and agents — so the graph is usable
40. Where is the official wording published for people (catalog /
    glossary), and what is only a copy?
41. What may a graph / meaning agent answer without reading a table or
    inventing a formula?
42. What must that agent refuse (calculate a crack from legs, treat a
    report column as the KPI, answer "who is the customer" without a
    role)?
43. How does in-platform assistance (Genie) get the same definition
    without becoming a second ontology?
44. If two sources disagree, which definition is authoritative, and how is
    that marked?
