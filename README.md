# Enterprise Performance Model

Documentation-and-architecture repository for a governed Downstream Oil & Gas performance model, plus a personal learning sandbox and two runnable Order-to-Cash demos.

The conceptual chain is the same in every track:

**objectives → value streams → capabilities → processes → measurements → KPIs → data products → models → consumption**

A widely used calculation is not automatically a KPI. Appearance in a register means planned in the controlled set; it does not prove a file exists.

## Start here

| If you want… | Open |
|---|---|
| GitHub orientation (this page) | [README.md](README.md) |
| Live Master Index — architecture map, artifact register, decisions, remapping | [EPM-FOUND-000 (Enablement Pack v2.3)](EPM_Project_Enablement_Pack_Markdown_HTML/EPM-FOUND-000.md) |
| Foundation architecture set (FOUND-001–006) | [EPM Foundation v2](EPM_Foundation_v2_Markdown_HTML/README.md) |
| Personal ontology / RDF / Neo4j / agents sandbox | [EPM_Homelab/00-Homelab-Charter-and-Roadmap.md](EPM_Homelab/00-Homelab-Charter-and-Roadmap.md) |
| Runnable unbilled-exposure demos | [demos/README.md](demos/README.md) |

## Three tracks

### 1. EPM — governed initiative

The Downstream O&G Enterprise Performance Model. Charter, operating model, foundation architecture, and the KPI Store workstream.

| Entry | Role |
|---|---|
| [EPM-FOUND-000](EPM_Project_Enablement_Pack_Markdown_HTML/EPM-FOUND-000.md) | **Canonical** Master Index (control panel + architecture map) |
| [EPM-FOUND-000A](EPM_Project_Enablement_Pack_Markdown_HTML/EPM-FOUND-000A_Architectural_Principles.md) | Architectural principles |
| [EPM-FOUND-001–006](EPM_Foundation_v2_Markdown_HTML/README.md) | Business, performance, semantic, ontology, measurement, and data-product architecture |
| [Project Enablement Pack](EPM_Project_Enablement_Pack_Markdown_HTML/README.md) | Instructions, operating model, onboarding, chat migration |
| [business_architecture/](business_architecture/) | Customer-domain problem statement, value-stream and data-product JSON |
| [ontology/](ontology/) | Enterprise KPI ontology (Turtle) and class-hierarchy notes |
| [ARCHIVE/](ARCHIVE/) | Superseded Charter and Register (old FOUND-001 / FOUND-002) |
| [best-practices/](best-practices/) | Teammate practice guides (not governed EPM artifacts) |

Reading copy of the visual handbook: [EPM_Integrated_Architecture_Handbook_Complete_Visuals_V2.html](EPM_Integrated_Architecture_Handbook_Complete_Visuals_V2.html) (V1 is superseded).

### 2. EPM_Homelab — personal learning sandbox

Intentionally mirrors EPM patterns. **Not a governed EPM artifact set.** Charter, ADRs, stack decisions, and a ten-phase (0–9) roadmap live under [`EPM_Homelab/`](EPM_Homelab/).

### 3. Demos — runnable O2C unbilled exposure

Three packs: full Databricks/Metric Views, a learner variant with an empty ontology stub, and a dbt/DuckDB/MetricFlow pack. See [`demos/README.md`](demos/README.md).

## Canonical sources

One live file per artifact. Other copies are stubs, pack-local maps, or superseded reading copies.

| Artifact | Canonical path | Other copies |
|---|---|---|
| Master Index (EPM-FOUND-000) | [`EPM_Project_Enablement_Pack_Markdown_HTML/EPM-FOUND-000.md`](EPM_Project_Enablement_Pack_Markdown_HTML/EPM-FOUND-000.md) | Root v0.1 stub; Foundation v2 pack map; HTML reading copies |
| Integrated Architecture Handbook | [`EPM_Integrated_Architecture_Handbook_Complete_Visuals_V2.html`](EPM_Integrated_Architecture_Handbook_Complete_Visuals_V2.html) | V1 superseded |
| Old Charter (former FOUND-001) | [`ARCHIVE/02_Project_Charter_and_Operating_Model.md`](ARCHIVE/02_Project_Charter_and_Operating_Model.md) | Superseded — do not treat as current FOUND-001 |
| Old Register (former FOUND-002) | [`ARCHIVE/03_Canonical_Artifact_Register_and_Chat_Migration_Playbook.md`](ARCHIVE/03_Canonical_Artifact_Register_and_Chat_Migration_Playbook.md) | Superseded — current FOUND-001/002 are the Foundation v2 architecture docs |

## Source precedence (highest first)

1. Approved canonical artifact
2. Approved decision-log entry
3. Approved specification
4. Current validated implementation
5. Candidate artifact
6. Working project chat
7. Prior / outside-project chat
8. Unvalidated Tableau XML or report logic
9. General industry assumption
