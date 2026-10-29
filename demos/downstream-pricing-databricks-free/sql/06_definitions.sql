-- 06_definitions.sql (added for E3, EPM-DEC-001-0109, decision 4): what the ontology says about each measure the
-- metric views implement, read from the projection's triple table, ${epm_triples}, which the projection driver writes
-- from the Turtle in git. One view lists every measure with a KPI or OPM identifier; one view per subject area keeps
-- the measures its metric views carry. They live in their own schema, ontology_definitions: they are plain views of
-- the ontology, not metric views, and the purge can drop them without touching the triple table, which the demo
-- does not own.

CREATE OR REPLACE VIEW ${catalog}.ontology_definitions.measure_definitions_vw AS
WITH t AS (
  SELECT subject, predicate, object, lang, graph FROM ${epm_triples}
  WHERE graph LIKE 'https://w3id.org/lsc/ontology/modules/kpi/%'
),
label AS (
  SELECT subject, graph, object AS Label FROM t
  WHERE predicate = 'http://www.w3.org/2004/02/skos/core#prefLabel' AND COALESCE(lang, 'en') = 'en'
),
measure AS (
  SELECT subject, graph, object AS Identifier FROM t
  WHERE predicate = 'http://purl.org/dc/terms/identifier'
    AND subject LIKE 'https://w3id.org/lsc/ontology/modules/kpi/measure/%'
),
confused AS (
  SELECT c.subject, c.graph, ARRAY_JOIN(ARRAY_SORT(COLLECT_LIST(l.Label)), '; ') AS Not_To_Be_Confused_With
  FROM t c JOIN label l ON l.subject = c.object AND l.graph = c.graph
  WHERE c.predicate = 'https://w3id.org/lsc/ontology/modules/kpi/notToBeConfusedWith'
  GROUP BY c.subject, c.graph
)
SELECT m.Identifier, l.Label, d.object AS Definition, g.object AS Grain, b.object AS Basis, c.Not_To_Be_Confused_With,
       kl.Label AS Kind, m.graph AS Release_Graph, m.subject AS Measure_Iri
FROM measure m
LEFT JOIN label l ON l.subject = m.subject AND l.graph = m.graph
LEFT JOIN t d ON d.subject = m.subject AND d.graph = m.graph AND d.predicate = 'http://www.w3.org/2004/02/skos/core#definition'
LEFT JOIN t g ON g.subject = m.subject AND g.graph = m.graph AND g.predicate = 'https://w3id.org/lsc/ontology/modules/kpi/grain'
LEFT JOIN t b ON b.subject = m.subject AND b.graph = m.graph AND b.predicate = 'https://w3id.org/lsc/ontology/modules/kpi/basis'
LEFT JOIN t k ON k.subject = m.subject AND k.graph = m.graph AND k.predicate = 'https://w3id.org/lsc/ontology/modules/kpi/measureKind'
LEFT JOIN label kl ON kl.subject = k.object AND kl.graph = m.graph
LEFT JOIN confused c ON c.subject = m.subject AND c.graph = m.graph;

-- Each subject area keeps the identifiers its metric views carry (sql/05_metric_views.sql); the pricing area also
-- keeps OPM-0026, which its view does not compute, so an agent can say what the measure is and why it has no value.
CREATE OR REPLACE VIEW ${catalog}.ontology_definitions.crack_spread_definitions_vw AS
SELECT * FROM ${catalog}.ontology_definitions.measure_definitions_vw WHERE Identifier IN ('KPI-0001');

CREATE OR REPLACE VIEW ${catalog}.ontology_definitions.executive_summary_definitions_vw AS
SELECT * FROM ${catalog}.ontology_definitions.measure_definitions_vw
WHERE Identifier IN ('KPI-0001', 'OPM-0017', 'OPM-0018', 'OPM-0019', 'OPM-0020', 'OPM-0021');

CREATE OR REPLACE VIEW ${catalog}.ontology_definitions.pricing_market_margin_definitions_vw AS
SELECT * FROM ${catalog}.ontology_definitions.measure_definitions_vw
WHERE Identifier IN ('OPM-0017', 'OPM-0018', 'OPM-0019', 'OPM-0020', 'OPM-0021', 'OPM-0026');

CREATE OR REPLACE VIEW ${catalog}.ontology_definitions.refinery_operations_definitions_vw AS
SELECT * FROM ${catalog}.ontology_definitions.measure_definitions_vw
WHERE Identifier IN ('OPM-0001', 'OPM-0002', 'OPM-0004', 'OPM-0005', 'OPM-0024', 'OPM-0025', 'OPM-0027');
