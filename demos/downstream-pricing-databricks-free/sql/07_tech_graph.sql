-- 07_tech_graph.sql (added for E5, EPM-DEC-001-0109, decision 7): the Delta copy of the technical graph, which
-- `python -m pricing_demo.tech_graph sync` fills from Neo4j, the graph's source. The build creates the tables empty, so
-- run the sync after every build. One row per node and per relationship; an edge whose target is an ontology resource
-- names its IRI, which the ontology's triple table also holds.

CREATE OR REPLACE TABLE ${catalog}.tech_graph.tech_graph_nodes (
  uri STRING COMMENT 'The node\'s IRI in the technical graph',
  kind STRING COMMENT 'Its class: Table, MetricView, PipelineStep, QualityCheck, Agent, Decision and so on',
  name STRING COMMENT 'The object, step, check or decision it stands for',
  properties STRING COMMENT 'Its other properties as JSON: rows, last refresh, a check\'s result',
  synced_at TIMESTAMP COMMENT 'When the sync copied it from Neo4j'
) COMMENT 'The technical graph\'s nodes, copied from Neo4j (EPM-DEC-001-0109, decision 7)';

CREATE OR REPLACE TABLE ${catalog}.tech_graph.tech_graph_edges (
  source STRING COMMENT 'The IRI of the node the relationship starts at',
  type STRING COMMENT 'The relationship type: READS_FROM, IMPLEMENTS, CHECKS, USED and so on',
  target STRING COMMENT 'The IRI of the node it ends at',
  target_in_ontology BOOLEAN COMMENT 'True when the target is an ontology resource rather than a technical-graph node',
  synced_at TIMESTAMP COMMENT 'When the sync copied it from Neo4j'
) COMMENT 'The technical graph\'s relationships, copied from Neo4j (EPM-DEC-001-0109, decision 7)';
