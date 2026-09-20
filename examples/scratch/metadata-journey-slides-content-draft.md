# Metadata Journey Slides — Content Draft (for review before design)

**Source of truth:** `master-use-case-kpi-store-semantic-governance.md` (working draft, treated as authoritative for this exercise per stakeholder instruction).
**Naming:** "ODPS" is presented as **Data Contract** (machine format unnamed on-slide). "Formula Pointer" is presented as **Measure Bind**. The "1:1 Governance Gate" is presented as the **Certification** step (intake & certification). Stage 4 is named **Data Product**.
**Audience discipline:** Slides avoid standards jargon (no ODPS, PROV-O, SKOS, `ekpi:`/`data:` prefixes). Business Architecture metadata is cited as **JSON** (not path + SHA). External-gap findings are quarantined in §3 Speaker Notes / Advisory — they do NOT appear on the slides.
**System conventions:** Four vendor platforms shown as visual anchors (ER/Studio, Unity Catalog, Bigeye, Microsoft Purview). Architecture components (KPI Store, Git Ontology / Graph of Meaning, Semantic Layer + Compiler, Data Contract) shown as styled text chips. Every metadata field carries its **birth system (SoR)** tag inline; catalog destinations (Purview / Unity Catalog) shown as small projections. KPI-stage metadata is shown as stored in the **Purview catalog**; the KPI Store remains the physical seat, cataloged in Purview.

---

## SLIDE 1 — "The Metadata Journey: From Domain Analysis to Certified Consumption"

**Subtitle strip:** "How metadata flows end to end — the stages a KPI moves through, the metadata each stage introduces, and the one system that owns it. Captured once at origin; referenced downstream by URI / IRI. Working draft."

### Top band — Journey buckets (5)

| Bucket | Stages | One-liner |
|---|---|---|
| **Domain & Meaning** | 1–2 | From business language to modeled domain and process context |
| **KPI Certification** | 3 | From candidate metric to certified Named KPI with a permanent Ontology IRI |
| **Build & Certify** | 4–5 | From physical ingredients to a compiled, certified measure |
| **Data Contract** | 6 | From certified measure to contracted data product |
| **Consume & Monitor** | 7 | From contract to governed consumption — and feedback |

*Visual: buckets 1–2 = Meaning Plane color; 3 = certification accent (boundary); 4–7 = Compute Plane color.*

### Middle band — 7 stage cards (each: number, name, 2–3 "what happens" bullets, key metadata with owner tags, footnote chips for participating-not-owning systems)

---

**① Domain Analysis & Definition** — *SoR: ER/Studio (CDM) + Git Turtle Ontology*

What happens: business terms and ubiquitous language are defined; domain boundaries and context established; the accountable executive (Tier 1 owner) is assigned.

Metadata introduced:
- Domain name & description — `ER/Studio CDM`
- Business terms / ubiquitous language definitions — `ER/Studio CDM` → formalized in `Git Turtle`
- Taxonomies & domain context — `Git Turtle` (SoT)
- Data classification (assigned here, enforced downstream) — `ER/Studio CDM`

Footnote chip: *→ Purview receives the business-glossary projection (discovery).*

---

**② Domain & Process Modeling** — *SoR: ER/Studio (LDM) + `business_architecture/`*

What happens: entities and relationships are modeled (CDM → LDM); value streams and process steps are documented; candidate KPIs are linked to process context ("used in").

Metadata introduced:
- Entities & relationships — `ER/Studio CDM/LDM`
- Attribute-level definitions — `ER/Studio LDM`
- Value stream names & process step IDs — `business_architecture/` (JSON)
- "Used in" process context — `business_architecture/` (JSON)

Footnote chip: *Process SoR is `business_architecture/` only — not `domain/`, not Turtle, not a SQL join key.*

---

**③ KPI Identification & Certification** — *SoR: Purview catalog · Git Turtle (IRI)*

What happens: the candidate enters the intake register; it is vetted for uniqueness against the Graph of Meaning; on certification it receives a permanent Ontology IRI — the steward verifies and the Domain Data Owner approves.

Metadata introduced (all stored in the Purview catalog):
- KPI business name & definition — `Purview`
- Ontology IRI — born in `Git Turtle` → stored in `Purview`
- Catalog status: `proposed | approved | drifted | archived` — `Purview`
- Measure Bind (abstract, versioned — never raw SQL) — `Purview`
- Steward & owner assignments (four tiers) — `Purview`
- Certification record — `Purview`

Footnote chip: *KPI Store is the physical seat; Purview catalogs the business metadata. Graph of Meaning exposed via Neo4j/Cypher.*

---

**④ Data Product** — *SoR: ER/Studio (PDM) + Databricks Silver*

What happens: PDM forward-engineers DDL; the Silver star schema (facts & dimensions) is built; a read-only copy of KPI metadata syncs one-way from the catalog for local joins.

Metadata introduced:
- Table schemas & column types — `ER/Studio PDM` → `Silver`
- Primary & foreign keys — `ER/Studio PDM`
- Grain keys & dimensionality — `ER/Studio PDM / Silver`
- Dimensional hierarchies — `Silver`
- KPI metadata read-only copy (one-way sync) — `from Purview`

Footnote chip: *Unity Catalog registers technical assets, access control, masking & row-level security. Purview/UC are catalogs — Purview holds the KPI business metadata.*

---

**⑤ Metric Compilation — Semantic Layer** — *SoR: Semantic Layer + Compiler*

What happens: the certified measure object is built and the Measure Bind resolves to it; the compiler validates against Silver ingredients, computes ad-hoc slices, and materializes Gold cuts at agreed grains.

Metadata introduced:
- Certified measure object name — `Semantic Layer` (Metric Views / dbt / Cube)
- Aggregation functions & filter constraints — `Semantic Layer`
- Available dimensions & joins — `Semantic Layer`
- Compile-time parameters — `Semantic Layer`
- Gold materialized cuts (no secondary client SUMs) — `Databricks Gold`

Footnote chip: *AI agents never author logic here — they submit the certified measure to the compiler; compiled SQL becomes the immutable audit trail.*

---

**⑥ Data Contract** — *SoR: Data Contract manifest (YAML, in Git)* — **visually an "assembly" card**

What happens: the automated metadata compiler merges semantic IRIs, physical schemas, and catalog properties into a generated contract; CI/CD parses the quality section and pushes rules to BigEye; the contract is versioned in Git.

*Assembled — rendered muted, each tagged with its source:*
- Ontology IRI ← Stage 3 · `Turtle`
- KPI identity, status, Measure Bind ← Stage 3 · `Purview`
- Schema, grain keys, column types ← Stage 4 · `PDM / Silver`
- Upstream lineage (source systems, Silver facts & dimensions) ← Stage 4
- Four-tier ownership ← Stages 1–3

*Born here — rendered in full color:*
- SLA / SLO commitments (freshness, latency, availability) — declared in contract; operational SoR = Databricks orchestration / SRE
- Output ports (SQL warehouse endpoint, REST API, Power BI semantic model) — declared here
- Certified vs prohibited uses & excluded data — SoR = Data Governance Board; enforced here
- DQ rule definitions — authored here, pushed to BigEye ("observability as code", bi-directional API)
- Version & change policy (SemVer; ≥90-day deprecation for breaking changes)

---

**⑦ Observability & Consumption** — *SoR: BigEye + Consuming Clients / Agents*

What happens: BigEye pulls the contract's rules via API, runs tests, and emits health scores; consumers and AI agents query only through certified output ports; every execution is captured as an audit trace; drift feeds the catalog status lifecycle.

Metadata introduced:
- Quality run metrics & test execution state — `BigEye`
- Freshness & anomaly detection results — `BigEye`
- Consumer queries (who queried what) — `Clients / AI Agents`
- Audit traces: run IDs, timestamps, SQL executed — `Databricks execution engine`
- Drift status — feeds back to `Purview / KPI Store` (status → `drifted`)

Footnote chip: *Purview carries the discovery projection, including KPI business metadata. Unity Catalog remains the technical catalog.*

### Bottom ribbon (slim — system flow, not a full band)

`ER/Studio` → `Git Ontology / Graph of Meaning` → `KPI Store` → `Unity Catalog (Silver/Gold)` → `Semantic Layer + Compiler` → `Data Contract (Git)` → `BigEye` → `Purview` → `Consumers & AI Agents`

Legend: Meaning Plane color | Compute Plane color | Certification accent (Stage 3) | SoR tag | Projection arrow (→ Purview / → UC)

---

## SLIDE 2 — "The Metadata Field Sets: What Sits Behind Each Stage"

**Subtitle:** "The full field set introduced at each stage — where each item is born (system of record) and where it is cataloged. Everything downstream references; nothing is re-keyed."

Seven columns (one per stage, same numbering and plane colors as Slide 1). Field format: **field** — `birth system (SoR)` → catalog destination.

### Column 1 — Domain Analysis & Definition *(anchor: ER/Studio)*

- Domain name & description — `ER/Studio CDM` → Purview
- Business terms / ubiquitous language — `ER/Studio CDM` → Turtle → Purview
- Taxonomies & domain context — `Git Turtle` → Purview
- Domain Data Owner (Tier 1) — `Purview identity` → Contract
- Data classification — `ER/Studio CDM` → Contract

### Column 2 — Domain & Process Modeling *(anchor: ER/Studio)*

- Entities & relationships — `ER/Studio CDM/LDM` → UC
- Attribute definitions — `ER/Studio LDM` → UC
- Value stream & process step IDs — `business_architecture/` (JSON) → Purview
- "Used in" process context — `business_architecture/` (JSON) → Purview

### Column 3 — KPI Identification & Certification *(anchors: Purview + Turtle)*

- KPI business name & definition — `Purview catalog`
- Ontology IRI — `Git Turtle` → Purview → Contract
- Catalog status (proposed | approved | drifted | archived) — `Purview catalog`
- Measure Bind (abstract, versioned) — `Purview catalog` → Contract
- Steward & four-tier owner identities — `Purview catalog`
- Certification record — `Purview catalog`

### Column 4 — Data Product *(anchors: ER/Studio + Unity Catalog)*

- Table & column names, data types — `ER/Studio PDM` → Silver → UC
- Primary / foreign keys — `ER/Studio PDM` → UC
- Grain keys & dimensionality — `PDM / Silver` → Contract
- Dimensional hierarchies — `Silver` → Semantic Layer
- KPI metadata read-only copy — `Purview` (1-way sync) → Silver

### Column 5 — Metric Compilation *(anchor: Semantic Layer chip)*

- Certified measure object name — `Semantic Layer` → Contract
- Aggregation functions & filter constraints — `Semantic Layer` → Purview / Contract
- Dimensions & joins — `Semantic Layer`
- Compile-time parameters — `Semantic Layer`
- Gold cuts at agreed grains — `Databricks Gold` (no secondary client SUMs)

### Column 6 — Data Contract *(anchor: contract chip; visually split assembled / born-here)*

*Assembled (by reference):* Ontology IRI (Turtle) · KPI identity, status, Measure Bind (Purview) · schema, grain, keys (PDM/Silver) · upstream lineage (Stage 4) · four-tier ownership (Stages 1–3)
*Born here:* SLA/SLO declarations (SoR: orchestration/SRE) · output ports · certified/prohibited uses, exclusions (SoR: Governance Board) · DQ rule definitions (pushed to BigEye) · version & change policy

### Column 7 — Observability & Consumption *(anchor: Bigeye + Purview)*

- DQ run metrics & test execution state — `BigEye` → Purview
- Freshness & anomaly results — `BigEye`
- Consumer queries — `Clients / AI Agents` → audit
- Audit traces (run IDs, SQL, timestamps) — `Databricks execution engine` → compliance logs
- Drift status — → `Purview / KPI Store` lifecycle

**Footer legend:** `tag` = born here (system of record) · → Purview = business catalog (incl. KPI metadata) · → UC = technical catalog · plane colors as Slide 1.

---

## Appendix — The Four-Tier Ownership Matrix (reference)

Every KPI carries four accountable owners so approval and delivery never bottleneck on one person. On the slides, the "four tiers" appear as the *Steward & four-tier owner identities* field at Stage 3 (stored in the Purview catalog) and the *Four-tier ownership* item assembled into the Data Contract at Stage 6.

| Tier | Role (who) | Accountable for |
|---|---|---|
| **1. Domain Data Owner** — *Strategic Authority* | Business Executive / Domain VP | Business glossary, domain boundaries; approves candidate KPI concepts and certified uses |
| **2. Data Product Owner** — *Product Lifecycle* | Lead Business Analyst / Metric Product Manager | Lifecycle of the KPI data product; authors the Data Contract; sets SLAs / SLOs |
| **3. Data Steward** — *Semantic Governance* | Senior Data Governance Specialist / Subject Expert | Runs certification (uniqueness verification); certifies the Ontology IRI; maps ER/Studio models; Purview setup |
| **4. Technical Owner** — *Compute & Pipeline* | Databricks Platform Engineer / Analytics Engineer | Silver star schema ETL; Semantic Layer / compiler configuration; BigEye monitoring setup |

**Promotion workflow (who acts when):**
1. **Data Product Owner** enters the candidate into the intake register (Stage 3)
2. **Data Steward** vets it against the Graph of Meaning and certifies it — Ontology IRI assigned — securing the **Domain Data Owner's** approval
3. **Technical Owner** builds the physical delivery at Stages 4–5 (Silver ingredients, certified measure, Measure Bind)
4. **Data Product Owner + Technical Owner** sign the Data Contract (Stage 6), which writes the catalog row and schedules the BigEye monitors

---

## §3 Speaker Notes / Advisory — NOT on slides

Findings from the external metadata-framework scan (OvalEdge, DataGalaxy, Atlan, ScienceDirect; data-contract standards). For the metadata-integration workstream's stakeholder advice on *what to capture and make available*; the draft does not yet assign owners — decisions needed:

1. **Compliance metadata depth** — draft covers classification and certified uses, but not retention rules or regulatory tags. Proposed home: capture at Stage 1 (classification), enforce at Stage 6 (contract). This is the most commonly skipped category in practice.
2. **Reference data & units of measure** — not staged in the draft; critical for KPIs (`crack_spread_per_bbl` needs currency + unit + hub enumerations). Draft hints via a mapped unit concept. Proposed: Stage 1/3 as governed domain concepts; owner unassigned — decision needed.
3. **Social / usage metadata** (popularity, access frequency, consuming reports) — the emerging "fifth category," and the signal AI agents use for asset recommendation. Proposed: Stage 7, flowing back into Purview.
4. **AI-readiness metadata** — the data-contract standard has moved two major versions past what the draft cites (2.1.0); agent-oriented ports are now defined by the standard. Proposed: Stage 6 contract fields + Stage 7 agent access. Flag version drift to the workstream.

---

*Change log: 2026-09-14 — stakeholder terminology pass: Stage 3 renamed "KPI Identification & Certification" (intake & certification; "1:1 gate" removed everywhere); Stage 4 renamed "Data Product"; "Formula Pointer" → "Measure Bind"; KPI-stage metadata shown stored in Purview catalog (KPI Store = physical seat); ODPS / PROV-O / SKOS / prefix jargon removed from slides; business architecture cited as JSON (not path + SHA); speaker-notes advisory rephrased to avoid naming standards.*
*Change log: 2026-09-14 — added Appendix "The Four-Tier Ownership Matrix" naming Tier 1 Domain Data Owner, Tier 2 Data Product Owner, Tier 3 Data Steward, Tier 4 Technical Owner, with the promotion workflow sequence, per stakeholder Q&A.*
