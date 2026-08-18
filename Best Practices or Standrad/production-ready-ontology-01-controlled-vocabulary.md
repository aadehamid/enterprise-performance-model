# Production-ready ontology - 01 Controlled vocabulary

| Field | Value |
| --- | --- |
| **Stage** | 1 of 6 - controlled vocabulary |
| **What this is** | Teammate practice guide. How to do the language work and what to land. First stage of the [production-ready ontology guide](production-ready-ontology-guide.md). |
| **What this is not** | Not a taxonomy, thesaurus, ontology, or knowledge graph. Not a planning deliverable. Not where you model the world. |
| **Date** | 2026-08-16 (America/Chicago) |
| **Landed** | 2026-08-16 10:13 CT. This is the teammate practice guide, not the 2026-08-15 short how-to. |
| **Audience** | Teammates who have not read the research or the chat. You should be able to do the language work from this file. |
| **Worked example** | Customer in order-to-cash. One rack lift. Live Demo 2 facts only. |

A controlled vocabulary is not where you model the world. Do the language work. Then stop. Later stages inherit this.

---

## 1. Who this is for / the name-everywhere problem

You are on a team that has to agree what words mean before anyone formalises an ontology or publishes a number. You have not been in the earlier chats. This file is how to do the language work.

The problem is simple: the same everyday word is used everywhere, and it does not mean one thing.

**One lift.** A rack lift for Apex can carry, on one bill of lading:

- who the product is sold to
- who settles the invoice
- who receives the invoice
- where it lifts (the terminal)
- who is allowed to lift at the rack

Every one of those may be called "customer" on a screen, a ticket, or a warehouse column. Sometimes the **same digits** show up in two fields. SAP `sold_to` `1000123` and SAP `bill_to` `1000123` are two roles. Warehouse `customer_id` `1000123` does not pick a role.

If you collapse those into one "customer," later Unbilled dollars land on the wrong object. The vocabulary exists so that does not happen.

## 2. What a CV is

A controlled vocabulary is a curated, finite list of approved terms. Each meaning records four things:

1. **Preferred label** - the one approved wording (Payer, Sold-To, Bill-To, Ship-To, Loading-Authorized Party).
2. **Aliases** - everyday variants, misspellings, and system codes that map to that wording. They do not compete with it. The word `customer` can be an alias on **two** IDs.
3. **Scope note** - one or two lines: what the term includes and what it excludes.
4. **`term_id`** - a stable ID (`id:payer`, `id:sold-to`, ...). Systems join on this. An IRI may bind later. The IRI does **not** replace `term_id`.

Light usage rules (capitalisation, singular vs plural) live next to the list. They are not a fifth competing label.

**A CV does not hold live keys.** `APEX-PAYER` and `CONS-4412` live in the map, not on the term row.

**A CV does not hold domain-model invariants.** It does not decide aggregates, bounded contexts, or whether Ship-To is a place in the model. It names the meaning. Modeling still models. A controlled vocabulary is one instrument inside domain modeling, not the method.

A list of words without preferred label, aliases, scope note, `term_id`, and a method is not a controlled vocabulary.


## Words we use

Read this once so the later tables do not feel like jargon.

| Word | What we mean |
| --- | --- |
| **Meaning** | A distinct idea, not the word on the screen. "Customer" is one word. Sold-To and Loading-Authorized Party are two meanings of that word. |
| **Word** | The string on a screen, ticket, or column (`customer`, `RG`, `APEX-PAYER`). One word can point at two meanings. |
| **Working group** | The people who pick the preferred label for a slice (commercial, credit, rack, invoicing). Data brings evidence. Data does not name the meaning. |
| **Preferred label** | The one approved wording. People read this. |
| **Alias** | An everyday word or code that maps to a `term_id`. It does not compete with the preferred label. The same alias can sit on two IDs when the word is overloaded. |
| **`term_id`** | The stable handle. Aliases and the map join on this. If the label later changes, the ID stays. |
| **Map** | `system + field + local_key` -> `term_id` (or no map). The number is the party. The column is the role. |
| **Scope note** | Includes and excludes for that meaning. Not a KPI grain, not a formula. |
| **`ontology_iri`** | A second name for the same meaning in the turtle file. It does not replace `term_id`. |

## 3. Purpose and scope

Decide which decisions the vocabulary must support, and name what is out of scope so the list does not sprawl.

**This slice supports:** agreeing language for Customer in order-to-cash so a later Unbilled number can slice on the right grains, and so search can say what a word or code means.

**Out of scope**

- Drawing an is-a tree
- Writing triples as the product
- Publishing a certified formula
- Renaming SAP, the lift system, or the warehouse in place
- Treating Unbilled as a customer class (Unbilled is a **state** of an obligation)

**On the lift.** Purpose is: keep sold-to, payer, bill-to, ship-to, and loading-authorized party distinct so "unbilled for this customer" is a real question. Out of scope is renaming the lift system's `CONS-4412` screen.

## 4. Word hunt - tables, columns, values

Start where the language already lives. Hunt **table names, column names, and the values in those columns**. Also hunt tickets, screens, and reports. Treat every hit as **evidence of a meaning, not an answer**. Expect noise.

**Unstructured / tagging first.** Ticket subjects, search logs, screen labels, report titles. People type `customer`, `lift customer`, `paying party`.

**Then structured seams.** Lookup tables, enumerations, dim values. Extract distinct values. Count frequencies. Read a slice of real rows so later choices rest on usage.

**On the lift (live Demo 2 hunt, not invented)**

| Where | Table / screen | Column | Value we actually have |
| --- | --- | --- | --- |
| Demo tickets | ticket row | `payer_id` | `APEX-PAYER` |
| Demo tickets | ticket row | `sold_to_id` | `APEX-HOU`, `APEX-DAL` |
| Demo tickets | ticket row | `bill_to_id` | `APEX-BILL` |
| Demo tickets | ticket row | `terminal_code` | `HSC` |
| Lift system | lift authorization | `lift_customer` | `CONS-4412` |
| SAP | partner functions | `sold_to` | `1000123` |
| SAP | partner functions | `bill_to` | `1000123` (same digits, different column) |
| Warehouse | `dim_customer` | `customer_id` | `1000123` |

The table name `dim_customer` is evidence. The column `customer_id` is evidence. The value `1000123` is evidence. None of them is the preferred label.

## 5. Cluster into meanings

Group the hits by **meaning**, not by the English word.

**On the lift, five meanings (working names until the working group signs the labels):**

| Meaning | What the lift is pointing at | What it is not |
| --- | --- | --- |
| Sold-To | Who the product is sold to (`APEX-HOU`, SAP `sold_to`) | Who pays; who may lift |
| Payer | Who settles the invoice (`APEX-PAYER`) | Sold-to; bill-to |
| Bill-To | Who receives the invoice (`APEX-BILL`) | Who pays (can differ) |
| Ship-To | Where it lifts (`HSC`) | A party role |
| Loading-Authorized Party | Who may lift at the rack (`CONS-4412`) | Sold-to; payer; site; the card/PIN token |

Warehouse `customer_id` `1000123` does **not** get its own meaning. It is an overloaded key. Park it as unresolved.

Do not fold these five into "Customer." That is the name-everywhere problem.

## 6. Choose the preferred label

The **working group** picks one preferred term per meaning. Evidence, not a vote of systems:

- **Docs** - contracts, invoices, deny codes, BOLs (how the writing already talks)
- **People** - what they search and say
- **Company need** - who is harmed if the wrong word wins (credit lives on the payer; lift deny lives on the loading-authorized party; Unbilled site grain lives on the terminal)

SAP codes (`AG`/`SP`, `RG`/`PY`) do not win. `dim_customer.customer_id` does not win.

**On the lift, the working group signed:**

| Meaning | Preferred label |
| --- | --- |
| Who the product is sold to | Sold-To |
| Who settles the invoice | Payer |
| Who receives the invoice | Bill-To |
| Where it lifts | Ship-To |
| Who may lift at the rack | Loading-Authorized Party |

Apply the same spelling and hyphenation everywhere. Do not crown one system's wording.

## 7. Scope notes

Write one or two lines per preferred label: includes / excludes. Tomorrow's editor and tomorrow's model should make the same decision.

**Landed on this lift** (`cv_term.scope_note`):

| `term_id` | Scope note |
| --- | --- |
| `id:payer` | Party that settles the invoice. Not sold-to or bill-to. |
| `id:sold-to` | Party the product is sold to. Not the payer and not a lift authorization. |
| `id:bill-to` | Party that receives the invoice. Not who settles it, and not who is entitled to lift. |
| `id:ship-to` | Delivery site / terminal. Not a party role. |
| `id:loading-authorized-party` | Who may lift at the rack. Not a payer, not a sold-to, and not a site. |

Loading-Authorized Party is **not** a certified Unbilled grain. Payer, Sold-To, and Ship-To are. Bill-To is mapped and still not an Unbilled grain.

## 8. Assign `term_id`

Mint a stable ID per meaning. Join keys (aliases, map rows) point at it. **Do not replace `term_id` with an IRI.** The IRI is a later bind on the same row.

**Landed IDs (do not invent others for this slice):**

- `id:payer`
- `id:sold-to`
- `id:bill-to`
- `id:ship-to`
- `id:loading-authorized-party`

If the preferred label later changes from "Payer" to "Invoice payer," the ID stays `id:payer`.

## 9. Aliases

Record every variant people and systems already use. Map each variant to exactly one `term_id` **unless the same string is truly two meanings**. Then it is two alias rows.

**On the lift:** the word `customer` is an alias on **both** `id:sold-to` and `id:loading-authorized-party`. Search must return both IDs. Never pick one and hide the other.

Live alias count: **22** rows. Partner-function codes (`AG`, `SP`, `RG`, `PY`, `RE`, `BP`, `WE`, `SH`) are aliases / notations, not preferred labels. `CONS-4412` is an alias of Loading-Authorized Party (and a live map key). `site` is an alias of Ship-To in this demo, not a second Customer meaning.

## 10. Map live keys

The map is the contract. Systems keep their local string. We do not rename SAP overnight.

Each row is:

`local_system` + `field` + `local_key` -> `term_id` (or no map)

**Same digits in two fields = two rows.** SAP `sold_to` `1000123` -> `id:sold-to`. SAP `bill_to` `1000123` -> `id:bill-to`. The number is the party. The column is the role.

**Warehouse `customer_id` `1000123` = no map.** Empty `term_id`, `map_ok = no`. The dim does not pick a role.

**On the lift (live rows you will see):**

| System | Field | Local key | `term_id` | Map? |
| --- | --- | --- | --- | --- |
| Demo2 | `payer_id` | `APEX-PAYER` | `id:payer` | yes |
| Demo2 | `sold_to_id` | `APEX-HOU` | `id:sold-to` | yes |
| Lift | `lift_customer` | `CONS-4412` | `id:loading-authorized-party` | yes |
| SAP | `sold_to` | `1000123` | `id:sold-to` | yes |
| SAP | `bill_to` | `1000123` | `id:bill-to` | yes |
| Warehouse | `customer_id` | `1000123` | (empty) | no |

Live map count: **19** rows (Demo2 payers / sold-tos / bill-tos / terminals, plus SAP, Lift, and the warehouse no-map).

GCA appears as payer, sold-to, **and** bill-to. Three rows. Same key, three fields, three meanings.

## 11. Short outward pass

Compare internal candidates to language partners already use. Import what clarifies. Keep internal phrasing as an alias when that is how people here talk.

**On this lift:** partner-function codes (sold-to / bill-to / payer / ship-to) and BOL header fields (consignee, bill-to, ship-to) clarify splits we already see. They do not become the preferred labels. Do not download a public "Customer" tree and call the hunt done. Cookie-cutter lists miss rack authorization.

## 12. Light governance

Before you treat the list as live:

- **Intake** is evidence (frequency, regulatory need, company need, demonstrated confusion), not opinion.
- **Working group** approves preferred labels and scope notes for the slice.
- **Version and deprecate** terms. Evolve the label. Keep `term_id` stable.
- **Pilot** in a real workflow. On this lift: search `customer` and confirm two IDs come back; run Unbilled `MEASURE()` for Apex payer and confirm it is not sliced on `CONS-4412` or warehouse `customer_id`.

A vocabulary that is not governed is a list that will sprawl again.

## 13. Artifacts to land

You write the **meaning** (preferred label, scope note, `term_id`, aliases, which live keys map). KPI Store Engineer checks the **objects** in the warehouse. Do not swap those seats.

Live pack (do not invent other counts or keys):

| Object | Columns / contract | Live Demo 2 |
| --- | --- | --- |
| `cv_term` | `term_id`, `preferred_label`, `scope_note`, `ontology_iri`. Join key = `term_id`. IRI does not replace `term_id`. | **5** rows |
| `cv_alias` | alias -> `term_id` | **22** rows. `customer` on `id:sold-to` **and** `id:loading-authorized-party` |
| `cv_map` | `local_system` + `field` + `local_key` -> `term_id` (or no map) | **19** rows. Warehouse `customer_id` `1000123` = no map |
| `cv_lookup(q)` | Matches `q` against alias **or** preferred_label / `term_id` **or** a mapped local_key. Not `dim_customer`. No dollars. No SQL rewrite. | search entry (function, or the documented JOIN) |
| `dim_customer` (optional decoy) | overloaded warehouse key | **1** row: `customer_id = 1000123`. `tickets.csv` is unchanged |

**IRI bind on `cv_term` (join key stays `term_id`)**

| `term_id` | `ontology_iri` |
| --- | --- |
| `id:payer` | `https://example.org/domain-ontology-kpi/o2c#Payer` |
| `id:sold-to` | `https://example.org/domain-ontology-kpi/o2c#SoldTo` |
| `id:bill-to` | `https://example.org/domain-ontology-kpi/o2c#BillTo` |
| `id:ship-to` | `https://example.org/domain-ontology-kpi/o2c#ShipTo` (not `#Site`) |
| `id:loading-authorized-party` | `https://example.org/domain-ontology-kpi/o2c#LoadingAuthorizedParty` |

Unbilled catalog about-ID stays `https://example.org/domain-ontology-kpi/o2c#UnbilledState`. That is a state, not a party class. Ship-To is `#ShipTo`, not `#Site`. Demo IRIs are unsigned and replaceable. These IRIs are a bind, not an ontology build.

**Why `cv_lookup` exists.** So a person or a search agent can ask "what is customer?" / "what is `APEX-PAYER`?" / "what is `CONS-4412`?" and get preferred label + `term_id` without touching a dollar and without rewriting anyone's SQL.

**Three paths**

1. **Raw SQL is honest.** `SELECT customer_id FROM dim_customer` still returns `1000123`. `tickets.csv` was not renamed. There is no interceptor.
2. **Published KPI only on mapped grains.** Unbilled `MEASURE()` groups on keys that map to Payer, Sold-To, or Ship-To. Apex payer is **$115,960.80 / 8**. `CONS-4412` is not a payer. Warehouse `customer_id` is not a dimension on that view.
3. **Search never a dollar.** Vocabulary search returns the two IDs for `customer` and never an Unbilled number.


**How `cv_lookup` works.** A string you type can live in three places. `customer` is an alias (on two IDs). `Payer` is a preferred label. `APEX-PAYER` is a map key, not an alias. If you only query `cv_term`, you miss most of them. The function is the one door: it searches alias **or** preferred label / `term_id` **or** a mapped `cv_map.local_key`, then joins back to `cv_term` for the label and scope note. It does **not** read `dim_customer`. It does **not** return a dollar. It does **not** rewrite anyone's SQL. If two meanings match, you get two rows. Hiding one is the bug.

| source | what it matches | `hit_kind` | example `q` |
| --- | --- | --- | --- |
| `cv_alias` | `alias` | `alias` | `customer`, `RG` |
| `cv_term` | preferred label or `term_id` | `label` | `Payer`, `id:payer` |
| `cv_map` | `local_key` where `term_id` is not null | `map_key` | `APEX-PAYER`, `CONS-4412` |

```sql
SELECT DISTINCT
  t.term_id,
  t.preferred_label,
  h.hit_kind,
  h.hit_value,
  t.scope_note
FROM (
  SELECT a.term_id, 'alias' AS hit_kind, a.alias AS hit_value
  FROM cv_alias a
  WHERE lower(a.alias) = lower(q)
  UNION ALL
  SELECT term.term_id, 'label' AS hit_kind,
    CASE
      WHEN lower(term.preferred_label) = lower(q) THEN term.preferred_label
      ELSE term.term_id
    END AS hit_value
  FROM cv_term term
  WHERE lower(term.preferred_label) = lower(q)
     OR lower(term.term_id) = lower(q)
  UNION ALL
  SELECT m.term_id, 'map_key' AS hit_kind, m.local_key AS hit_value
  FROM cv_map m
  WHERE m.term_id IS NOT NULL
    AND lower(m.local_key) = lower(q)
) h
INNER JOIN cv_term t ON t.term_id = h.term_id
```

`hit_kind` is how the string matched (`alias`, `label`, `map_key`). `hit_value` is the string that matched. The answer is `term_id` + preferred label.

| column | what it is |
| --- | --- |
| `term_id` | The meaning that matched |
| `preferred_label` | Approved wording from `cv_term` |
| `hit_kind` | How the string matched: `alias`, `label`, or `map_key` |
| `hit_value` | The actual string that matched |
| `scope_note` | Includes / excludes, from `cv_term` |


**Two Genie agents stay side by side** (Sidebar -> Genie Agents).

| Title | Sources | Job | "What is customer?" |
| --- | --- | --- | --- |
| `O2C certified KPIs` | Three Metric Views only. No `cv_*`. | Dollars via `MEASURE()` | Guesses, or asks you to name payer / sold_to / site. No map. That contrast is the point. |
| `O2C vocabulary search` | `cv_term`, `cv_alias`, `cv_map` only | Preferred label + `term_id`. Never a dollar. | Runs `cv_lookup('customer')`, returns both IDs, says the word is overloaded. |

Do not attach `cv_*` to the certified agent. Do not attach Metric Views to the search agent.

**Paste-ready checks** (`workspace.o2c_unbilled`):

```sql
SELECT term_id, preferred_label, ontology_iri
FROM workspace.o2c_unbilled.cv_term
ORDER BY term_id;

SELECT * FROM workspace.o2c_unbilled.cv_lookup('customer');
-- two IDs: id:sold-to and id:loading-authorized-party

SELECT term_id, preferred_label FROM workspace.o2c_unbilled.cv_lookup('RG');
SELECT term_id, preferred_label FROM workspace.o2c_unbilled.cv_lookup('APEX-PAYER');
SELECT term_id, preferred_label FROM workspace.o2c_unbilled.cv_lookup('CONS-4412');

SELECT local_system, field, local_key, term_id, map_ok, note
FROM workspace.o2c_unbilled.cv_map
ORDER BY local_system, field, local_key;
-- 19 rows; warehouse 1000123 has no term_id

SELECT payer, MEASURE(unbilled_usd), MEASURE(unbilled_ticket_count)
FROM workspace.o2c_unbilled.unbilled_usd
WHERE payer = 'Apex Fuels LLC'
GROUP BY payer;
-- 115960.80 / 8

-- must fail
SELECT customer_id, MEASURE(unbilled_usd)
FROM workspace.o2c_unbilled.unbilled_usd
WHERE customer_id = '1000123'
GROUP BY customer_id;

SELECT loading_authorized_party, MEASURE(unbilled_usd)
FROM workspace.o2c_unbilled.unbilled_usd
GROUP BY loading_authorized_party;

SELECT customer_id FROM workspace.o2c_unbilled.dim_customer;
-- 1000123

SELECT 'cv_term' AS seat, term_id AS key, preferred_label AS label, ontology_iri
FROM workspace.o2c_unbilled.cv_term
WHERE ontology_iri IS NOT NULL
UNION ALL
SELECT 'catalog', kpi_id, name, ontology_iri
FROM workspace.o2c_unbilled.dim_kpi_metadata
WHERE ontology_iri LIKE '%#UnbilledState';
```

## 14. Done enough / stop

A slice is ready to leave stage 1 when:

- Purpose and out-of-scope are written down
- Each in-scope meaning has preferred label + aliases + scope note + `term_id`
- Live keys that matter are mapped (or explicitly no-map)
- Search returns both IDs for an overloaded word
- Published numbers only slice on mapped grains
- Intake, approval, version, and deprecate are named

Then stop.

Do not draw the is-a tree. Do not write a thesaurus of related terms as the product. Do not declare classes beyond the meaning bind already on `cv_term`. Do not stand up a knowledge graph.

Later stages (metadata standards, taxonomy, thesaurus, ontology, knowledge graph) inherit this language. They inherit whatever mess you skip here.

On this lift you stop when Sold-To, Payer, Bill-To, Ship-To, and Loading-Authorized Party are distinct, `customer` hits two IDs, warehouse `1000123` has no map, and Unbilled Apex payer is still $115,960.80 / 8 on the payer grain.

## How a teammate starts

1. Write purpose and out-of-scope for the slice.
2. Hunt table names, column names, and values (plus tickets, screens, reports). Treat hits as evidence.
3. Cluster by meaning. Do not fold Sold-To, Payer, Bill-To, Ship-To, and Loading-Authorized Party into "Customer."
4. Working group picks preferred labels and scope notes. Data does not name the meaning.
5. Assign `term_id`. Record aliases. Build the map as `system + field + key`. Same digits in two fields are two rows. A warehouse key with no role is no map.
6. Land `cv_term`, `cv_alias`, `cv_map`, and `cv_lookup`. Optional: a `dim_customer` decoy so raw SQL stays honest.
7. Use the three paths: raw SQL is honest; published KPIs slice only on mapped grains; search never a dollar.
8. Bind `ontology_iri` when the meaning file exists. Do not replace `term_id`. Unbilled catalog stays `#UnbilledState`.
9. Stop. Do not draw a class tree. Domain modeling still does the rest.

