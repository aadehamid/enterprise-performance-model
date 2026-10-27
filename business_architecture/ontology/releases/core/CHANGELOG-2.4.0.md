# core changelog

## 2.4.0 (2026-10-26)

A minor release: it renames concepts and adds statements, and adds or removes no IRI. Built from the released 2.3.0 graph; 2.3.0 is unchanged. It carries the one process-map change merged since 2.3.0 was built, MPC-P12 (EPM-DEC-001-0105), read from the map at commit 4906666, and core's qSKOS fixes (EPM-DEC-001-0098, items 2 and 5). Claude approved it under the decision owner's delegation (EPM-DEC-001-0028, amendment of 2026-10-25, evening; EPM-DEC-001-0105).

- [minor] **25 processes renamed by their parent (MPC-P12).** The map gave them seven shared names. The four steps of each analysis under CM 1.3.1 now name the analysis (for example "Analyze Market Data" and "Document Findings of Market Analysis"); the two Determine Taxability steps are "Determine Invoice Taxability" (CM 1.3.8.1.3) and "Determine Taxability for Reporting" (CM 1.3.8.4.5); the two XPIMS steps name the evaluation they support (CM 1.1.2.6.1, CM 1.1.2.7.1); and CM 1.2.3.1 is "Perform Actualizations". Each old name is kept as `core:priorPreferredLabel`, with a change note.
- [minor] **Four alternative labels moved to `core:priorPreferredLabel`** on CM 1.3.2.3.1 to CM 1.3.2.3.4, because each equals the preferred label of a process under CM 1.3.2.2 (EPM-DEC-001-0098, item 2).
- [minor] **Core's eleven code lists state their top concepts.** Each member of `core:ApqcMappingDecision`, `core:BusinessDomain`, `core:Cadence`, `core:ConceptKind`, `core:EvidenceBases`, `core:GovernanceStatus`, `core:HoldStatus`, `core:LifecycleStatus`, `core:OperatingMode`, `core:PlanningLevel` and `core:ScopeUnits` is `skos:topConceptOf` its list, and the list `skos:hasTopConcept` it (EPM-DEC-001-0098, item 5).
- The shapes and the canonical-fact mapping are 2.3.0's, unchanged.
