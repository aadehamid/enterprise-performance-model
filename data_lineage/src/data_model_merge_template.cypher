// ===========================================================================
// DATA MODEL TEMPLATE
// ===========================================================================

// ---------------------------------------------------------------------------
// 1. CONSTRAINTS
//    NODE KEY or UNIQUENESS stays in place.
//    IS NOT NULL constraints sit beside UNIQUE keys so a null cannot bypass them.
// ---------------------------------------------------------------------------
CREATE CONSTRAINT BusinessArea_name_key        IF NOT EXISTS FOR (n:BusinessArea)        REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT BusinessProcess_name_key     IF NOT EXISTS FOR (n:BusinessProcess)     REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT BusinessTerm_name_key        IF NOT EXISTS FOR (n:BusinessTerm)        REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT CapabilityDataDomain_name_key IF NOT EXISTS FOR (n:CapabilityDataDomain) REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT Column_qualifiedName_key     IF NOT EXISTS FOR (n:Column)              REQUIRE n.qualifiedName IS UNIQUE;
CREATE CONSTRAINT Column_qualifiedName_exists  IF NOT EXISTS FOR (n:Column)              REQUIRE n.qualifiedName IS NOT NULL;
CREATE CONSTRAINT DataModel_name_key            IF NOT EXISTS FOR (n:DataModel)           REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT DataPipeline_name_key        IF NOT EXISTS FOR (n:DataPipeline)        REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT DataProductLine_name_key     IF NOT EXISTS FOR (n:DataProductLine)     REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT DataProduct_name_key         IF NOT EXISTS FOR (n:DataProduct)         REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT DataSystem_name_key          IF NOT EXISTS FOR (n:DataSystem)          REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT Legacy_qualifiedName_key     IF NOT EXISTS FOR (n:Legacy)              REQUIRE n.qualifiedName IS NODE KEY;
CREATE CONSTRAINT MasterDataDomain_name_key    IF NOT EXISTS FOR (n:MasterDataDomain)    REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT MasterDataDomain_name_exists IF NOT EXISTS FOR (n:MasterDataDomain)    REQUIRE n.name IS NOT NULL;
CREATE CONSTRAINT Person_name_key              IF NOT EXISTS FOR (n:Person)              REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT Policy_type_key              IF NOT EXISTS FOR (n:Policy)              REQUIRE n.type IS NODE KEY;
// Report_name_key was dropped. Two reports may share a display name.
// Rollback: CREATE CONSTRAINT Report_name_key IF NOT EXISTS FOR (n:Report) REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT Report_reportKey_key         IF NOT EXISTS FOR (n:Report)              REQUIRE n.reportKey IS NODE KEY;
CREATE CONSTRAINT RoleAssignment_key           IF NOT EXISTS FOR (n:RoleAssignment)      REQUIRE (n.type, n.scope) IS UNIQUE;
CREATE CONSTRAINT RoleAssignment_type_exists   IF NOT EXISTS FOR (n:RoleAssignment)      REQUIRE n.type IS NOT NULL;
CREATE CONSTRAINT RoleAssignment_scope_exists  IF NOT EXISTS FOR (n:RoleAssignment)      REQUIRE n.scope IS NOT NULL;
CREATE CONSTRAINT Server_serverName_key        IF NOT EXISTS FOR (n:Server)              REQUIRE n.serverName IS NODE KEY;
CREATE CONSTRAINT SubBusinessArea_name_key     IF NOT EXISTS FOR (n:SubBusinessArea)     REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT TableSchemaVersion_name_key  IF NOT EXISTS FOR (n:TableSchemaVersion)  REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT Table_qualifiedName_key      IF NOT EXISTS FOR (n:Table)               REQUIRE n.qualifiedName IS UNIQUE;
CREATE CONSTRAINT Table_qualifiedName_exists   IF NOT EXISTS FOR (n:Table)               REQUIRE n.qualifiedName IS NOT NULL;
CREATE CONSTRAINT Schema_qualifiedName_key     IF NOT EXISTS FOR (n:Schema)              REQUIRE n.qualifiedName IS NODE KEY;
CREATE CONSTRAINT FlatFile_name_key            IF NOT EXISTS FOR (n:FlatFile)            REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT UseCase_description_key      IF NOT EXISTS FOR (n:UseCase)             REQUIRE n.description IS NODE KEY;
CREATE CONSTRAINT ValueStreamStage_name_key    IF NOT EXISTS FOR (n:ValueStreamStage)    REQUIRE n.name IS NODE KEY;
CREATE CONSTRAINT Session_id_key              IF NOT EXISTS FOR (n:Session)             REQUIRE n.id IS NODE KEY;
CREATE CONSTRAINT DataSystem_isSoxRelevant_bool IF NOT EXISTS FOR (n:DataSystem) REQUIRE n.isSoxRelevant IS :: BOOLEAN;
CREATE CONSTRAINT DataSystem_isRecordActive_bool IF NOT EXISTS FOR (n:DataSystem) REQUIRE n.isRecordActive IS :: BOOLEAN;
CREATE CONSTRAINT DataSystem_description_string IF NOT EXISTS FOR (n:DataSystem) REQUIRE n.description IS :: STRING;
CREATE CONSTRAINT Policy_isSoxRelevant_bool    IF NOT EXISTS FOR (n:Policy)              REQUIRE n.isSoxRelevant IS :: BOOLEAN;

// ---------------------------------------------------------------------------
// 2. ADDITIONAL INDEXES  (beyond those auto-created by constraints)
// ---------------------------------------------------------------------------
CREATE FULLTEXT INDEX ft_business_names IF NOT EXISTS
  FOR (n:BusinessArea|CapabilityDataDomain|BusinessProcess|DataProduct|DataProductLine|BusinessTerm|ValueStreamStage|Report)
  ON EACH [n.name];

CREATE INDEX idx_datapipeline_trigger  IF NOT EXISTS FOR (n:DataPipeline)    ON (n.trigger);
CREATE INDEX idx_roleassignment_type   IF NOT EXISTS FOR (n:RoleAssignment)  ON (n.type, n.status);
CREATE INDEX idx_table_schema          IF NOT EXISTS FOR (n:Table)           ON (n.schema);
CREATE INDEX idx_table_layer           IF NOT EXISTS FOR (n:Table)           ON (n.layer);

// ---------------------------------------------------------------------------
// 3. NODE LABELS & PROPERTIES  (27 labels — counts as of 2026-04-15)
// ---------------------------------------------------------------------------
//
//  :BusinessArea (7)
//    name, description, createdAt
//
//  :BusinessProcess (12)
//    name, description, sequenceLabel
//
//  :BusinessTerm (0)
//    (no properties populated yet)
//
//  :CapabilityDataDomain (18)
//    name, description, createdAt
//
//  :Column (17701)
//    qualifiedName, name, dataType, sourceDataType, keyType,
//    definition, transformation, sourceFile
//
//  :DataModel (42)
//    name, fileName, modelType, folderLink, sourceFile, createdAt, updatedAt
//    modelType = 'Conceptual' | 'Logical'
//
//  :DataPipeline (0)
//    (no properties populated yet)
//
//  :DataProduct (12)
//    name, sourceFile, createdAt
//
//  :DataProductLine (4)
//    name
//
//  :DataSystem (219)
//    name, systemId, platform, applicationType, applicationService,
//    ingestionMethod, dataModality, refreshFrequency,
//    purviewReplicaSchemaName, purviewSourceTypeAssetLink,
//    confidentialityClassification, isSoxRelevant (boolean), isRecordActive (boolean),
//    role, scope, status, description, createdAt, updatedAt
//
//  :Dimension (58)
//    qualifiedName, name, layer, comment, sourceDataSystem,
//    sourceFile, createdAt, updatedAt
//
//  :Fact (48)
//    qualifiedName, name, layer, sourceFile, createdAt, updatedAt
//
//  :FlatFile (1)
//    name, createdAt
//
//  :MasterDataDomain (11)
//    name, status, sourceFile, createdAt, updatedAt
//
//  :Person (14)
//    name, createdAt
//
//  :Policy (2)
//    type, description, confidentialityClassification,
//    isSoxRelevant, createdAt
//
//  :Report
//    reportKey (webUrl when set, otherwise name: plus name), name, webUrl,
//    connectionType, sourceFile, createdAt
//
//  :RoleAssignment (799)
//    type, scope, status, createdAt
//    type = 'Data Analyst' | 'Data Analyst Backup'
//    scope = qualifiedName of the Table/View the role applies to
//
//  :Schema (87)
//    qualifiedName, name, layer, role, sourceType,
//    isCrossCutting, refactorTarget, createdAt, updatedAt
//
//  :Server (22)
//    serverName, createdAt
//
//  :SubBusinessArea (0)
//    (no properties populated yet)
//
//  :Table (3922)
//    qualifiedName, name, tableName, layer, comment,
//    sourceDataSystem, sourceFile, sttmLink, tableauReportEntity,
//    viewDefinition, createdAt, updatedAt
//
//  :Legacy (116 — 110 Tables + 6 Schemas)
//    Multi-label for pre-standard schema objects (dwh, dwh_core, persistence,
//    staging; src/medallion.py has the full list). NOT a layer value. Query: MATCH (t:Table:Legacy)
//    qualifiedName (same as the underlying Table or Schema node)
//
//  :TableSchemaVersion (0)
//    (no properties populated yet)
//
//  :UseCase (0)
//    (no properties populated yet)
//
//  :ValueStreamStage (3)
//    name, description, sequenceOrder
//
//  :View (58)
//    qualifiedName, name, layer, sourceFile, sttmLink,
//    tableauReportEntity, viewDefinition, createdAt, updatedAt
//
//  :Session
//    id
//
//  :Message
//    question, cypher, answer, timestamp, feedback, feedbackComment
//

// ---------------------------------------------------------------------------
// 4. RELATIONSHIP PATTERNS  (22 types — source → target with counts)
// ---------------------------------------------------------------------------
//
//  --- Data Lineage ---
//  (:Table)-[:DERIVED_FROM]->(:Table)                    x2283
//  (:Column)-[:DERIVED_FROM]->(:Column)                  x7555
//  (:Table)-[:REPLICATED_TO]->(:Table)                   x1442
//  (:Table)-[:HAS_COLUMN]->(:Column)                     x17281
//  (:Table)-[:MIGRATED_FROM]->(:DataSystem)              x9     // Gold table sourced from Alteryx Sandbox
//  (:Table)-[:REFACTORED_TO]->(:Table)                   x89    // Legacy → IDP Silver
//  (:DataSystem)-[:MIGRATED_TO]->(:Table)                x110
//
//  --- Infrastructure ---
//  (:Server)-[:HOSTS]->(:DataSystem)                     x28
//  (:DataSystem)-[:HOSTS]->(:Schema)                     x18
//  (:DataSystem)-[:CONTAINS]->(:Table)                   x1489  // Operational tables
//  (:DataSystem)-[:REPLICATED_TO]->(:Schema)             x9
//  (:Schema)-[:CONTAINS]->(:Table)                       x2408
//  (:FlatFile)-[:CONTAINS]->(:Table)                     x13
//  (:DataSystem)-[:SUBJECT_TO]->(:Policy)                x15
//
//  --- Consumption ---
//  (:Report)-[:CONSUMES]->(:Table)                       x543
//  (:DataProduct)-[:REALIZED_BY]->(:Table)               x351
//  (:MasterDataDomain)-[:REALIZED_IN]->(:Table)          x160
//
//  --- Role Assignments ---
//  (:Person)-[:HAS_ROLE]->(:RoleAssignment)              x799
//  (:RoleAssignment)-[:APPLIES_TO]->(:Table)             x799
//
//  --- Business Context ---
//  (:DataSystem)-[:BELONGS_TO]->(:BusinessArea)          x217
//  (:Schema)-[:BELONGS_TO]->(:BusinessArea)              x4
//  (:Report)-[:BELONGS_TO]->(:CapabilityDataDomain)      x125
//  (:DataProduct)-[:BELONGS_TO]->(:CapabilityDataDomain) x12
//  (:DataModel)-[:MODELS]->(:CapabilityDataDomain)       x40
//  (:DataModel)-[:BELONGS_TO]->(:DataSystem)               x20
//  (:DataProductLine)-[:OWNS]->(:CapabilityDataDomain)   x17
//  (:CapabilityDataDomain)-[:SUPPORTS]->(:BusinessProcess) x46
//  (:BusinessProcess)-[:BELONGS_TO_STAGE]->(:ValueStreamStage) x12
//  (:BusinessProcess)-[:INFORMS]->(:BusinessProcess)     x1
//  (:BusinessArea)-[:HAS_PRODUCT_LINE]->(:DataProductLine) x4
//  (:BusinessArea)-[:HAS_STAGE]->(:ValueStreamStage)     x3
//  (:ValueStreamStage)-[:NEXT_STAGE]->(:ValueStreamStage) x2
//  (:ValueStreamStage)-[:LOOPS_BACK_TO]->(:ValueStreamStage) x1
//
//  --- Conversation History & Feedback ---
//  (:Session)-[:HAS_MESSAGE]->(:Message)
//  (:Session)-[:LAST_MESSAGE]->(:Message)
//  (:Message)-[:NEXT]->(:Message)
//

// ---------------------------------------------------------------------------
// 5. SAMPLE MERGE — visual model seed (replace PH_ with real values)
// ---------------------------------------------------------------------------

// Infrastructure tier
MERGE (srv:Server         {serverName: "PH_Server"})
MERGE (ds:DataSystem      {name: "PH_DataSystem"})
MERGE (sch:Schema         {qualifiedName: "PH_Schema"})
MERGE (srv)-[:HOSTS]->(ds)
MERGE (ds)-[:HOSTS]->(sch)

// Operational → Replica → Silver/Gold → Semantic
MERGE (op:Table   {qualifiedName: "PH_Op_Table",       layer: "Operational"})
MERGE (rep:Table  {qualifiedName: "PH_Rep_Table",      layer: "Replica"})
MERGE (slv:Table  {qualifiedName: "PH_Silver_Table",   layer: "Silver"})
MERGE (gold:Table {qualifiedName: "PH_Gold_Table",     layer: "Gold"})
MERGE (sem:Table  {qualifiedName: "PH_Semantic_View",  layer: "Semantic"})

MERGE (ds)-[:CONTAINS]->(op)
MERGE (sch)-[:CONTAINS]->(rep)
MERGE (op)-[:REPLICATED_TO]->(rep)
MERGE (slv)-[:DERIVED_FROM]->(rep)
MERGE (gold)-[:DERIVED_FROM]->(slv)
MERGE (sem)-[:DERIVED_FROM]->(gold)

// Column-level lineage
MERGE (col1:Column {qualifiedName: "PH_Rep_Col"})
MERGE (col2:Column {qualifiedName: "PH_Silver_Col"})
MERGE (rep)-[:HAS_COLUMN]->(col1)
MERGE (slv)-[:HAS_COLUMN]->(col2)
MERGE (col2)-[:DERIVED_FROM]->(col1)

// Flat file source
MERGE (ff:FlatFile {name: "PH_FlatFile"})
MERGE (ffOp:Table  {qualifiedName: "PH_FF_Op", layer: "Operational"})
MERGE (ff)-[:CONTAINS]->(ffOp)

// Consumption
MERGE (rpt:Report      {reportKey: "name:PH_Report"})
SET rpt.name = "PH_Report"
MERGE (dp:DataProduct   {name: "PH_DataProduct"})
MERGE (rpt)-[:CONSUMES]->(sem)
MERGE (dp)-[:REALIZED_BY]->(sem)

// Master Data Domain
MERGE (mdd:MasterDataDomain {name: "PH_MasterDataDomain"})
MERGE (mdd)-[:REALIZED_IN]->(slv)

// Migration & Refactoring
MERGE (sandbox:DataSystem {name: "PH_Alteryx_Sandbox"})
MERGE (gold)-[:MIGRATED_FROM]->(sandbox)
MERGE (legacy:Table:Legacy {qualifiedName: "PH_Legacy"})
SET legacy.layer = "Silver"  // layer = correct medallion layer; :Legacy label = provenance
MERGE (legacy)-[:REFACTORED_TO]->(slv)

// Policy
MERGE (pol:Policy {type: "PH_PolicyType"})
MERGE (ds)-[:SUBJECT_TO]->(pol)

// Business Context hierarchy
MERGE (ba:BusinessArea              {name: "PH_BusinessArea"})
MERGE (dpl:DataProductLine          {name: "PH_DataProductLine"})
MERGE (cdd:CapabilityDataDomain     {name: "PH_CapabilityDomain"})
MERGE (bp:BusinessProcess           {name: "PH_BusinessProcess"})
MERGE (vs1:ValueStreamStage         {name: "PH_Stage_1"})
MERGE (vs2:ValueStreamStage         {name: "PH_Stage_2"})

MERGE (ba)-[:HAS_PRODUCT_LINE]->(dpl)
MERGE (ba)-[:HAS_STAGE]->(vs1)
MERGE (dpl)-[:OWNS]->(cdd)
MERGE (cdd)-[:SUPPORTS]->(bp)
MERGE (bp)-[:BELONGS_TO_STAGE]->(vs1)
MERGE (vs1)-[:NEXT_STAGE]->(vs2)
MERGE (dp)-[:BELONGS_TO]->(cdd)
MERGE (rpt)-[:BELONGS_TO]->(cdd)
MERGE (ds)-[:BELONGS_TO]->(ba)

// Role Assignments
MERGE (per:Person              {name: "PH_Analyst"})
MERGE (ra:RoleAssignment       {type: "Data Analyst", scope: "PH_Semantic_View"})
ON CREATE SET ra.status = 'Active', ra.createdAt = datetime()
MERGE (per)-[:HAS_ROLE]->(ra)
MERGE (ra)-[:APPLIES_TO]->(sem)

// Data Pipelines (ETL)
MERGE (pipeline:DataPipeline {name: "PH_SynapsePipelineName"})
ON CREATE SET pipeline.synapseDataflow = "PH_SynapseDataflowName",
              pipeline.alteryxWorkflow = "PH_AlteryxWorkflowName.yxmd",
              pipeline.sourceFile = "PH_SourceFile.xlsx",
              pipeline.createdAt = datetime()
ON MATCH SET pipeline.updatedAt = datetime()
MERGE (pipeline)-[:READS]->(replica_t)     // DataPipeline reads from Replica tables
MERGE (pipeline)-[:LOADS]->(gold_t)        // DataPipeline loads into Gold tables

// Data Model Artifacts (ER Studio .DM1 files)
MERGE (dm:DataModel {name: "PH_DataModelName"})
ON CREATE SET dm.fileName  = "PH_DataModelName.DM1",
              dm.modelType = "Conceptual",  // or "Logical"
              dm.folderLink = "PH_FolderLink",
              dm.sourceFile = "PH_SourceFile.xlsx",
              dm.createdAt = datetime()
ON MATCH SET dm.updatedAt = datetime()
MERGE (dm)-[:MODELS]->(cdd)                // DataModel models a CapabilityDataDomain
MERGE (dm)-[:BELONGS_TO]->(ds)             // DataModel belongs to a specific DataSystem

// Conversation History & Feedback Merge Templates
MERGE (sess:Session {id: "PH_SessionId"})
CREATE (msg:Message {
    question: "PH_UserQuestion",
    cypher: "PH_CypherUsed",
    answer: "PH_NarrativeAnswer",
    timestamp: datetime()
})
MERGE (sess)-[:HAS_MESSAGE]->(msg)
MERGE (sess)-[:LAST_MESSAGE]->(msg)

