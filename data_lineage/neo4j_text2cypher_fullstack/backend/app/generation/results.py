"""Pure transforms from Neo4j result records to the payload the portal renders."""
import ast

import neo4j

# Medallion lineage grid: row key -> column header, in display order.
MEDALLION_COLUMNS = {
    "srv": "Server",
    "ds": "Data System",
    "op": "Operational Source",
    "replica": "Replica",
    "silver": "Silver",
    "gold": "Gold",
    "semantic": "Semantic",
    "rpt": "Report",
    "owner": "Data Analyst",
}
# First matching label wins, so the order is the bucketing priority.
_LABEL_COLUMN = {"Server": "srv", "DataSystem": "ds", "FlatFile": "ds", "Report": "rpt", "Person": "owner"}
_TABLE_LABELS = {"Table", "View", "Dimension", "Fact", "Legacy"}
_LAYER_COLUMN = {"operational": "op", "replica": "replica", "silver": "silver", "gold": "gold", "semantic": "semantic"}
_MEDALLION_LABELS = {"Server", "DataSystem", "FlatFile", "Table", "View", "Report", "Person"}
_NON_MEDALLION_LABELS = {
    "Column", "DataModel", "CapabilityDataDomain", "DataProduct", "MasterDataDomain",
    "BusinessArea", "BusinessProcess", "DataPipeline",
}

_DEFAULT_HEADERS = {
    **{k: MEDALLION_COLUMNS[k] for k in ("srv", "ds", "op", "rpt", "owner")},
    "report": "Report",
    "dataanalyst": "Data Analyst",
    "ra": "Role Assignment",
    "roleassignment": "Role Assignment",
}
_EXCLUDED_KEYS = {"ra", "roleassignment", "df", "derivation", "uppath", "c1", "h", "con", "hr", "at"}
_CONFORMED_ORDER = ["srv", "ds", "op", "upstream", "rpl", "t", "downstream", "rpt", "report", "owner", "dataanalyst"]

_INTENTS = [
    (["capability data domain", "portfolio", "subject area"], ["CapabilityDataDomain"], "Capability Data Domain"),
    (["master data domain"], ["MasterDataDomain"], "Master Data Domain"),
    (["domain"], ["CapabilityDataDomain", "MasterDataDomain"], "Data Domain"),
    (["report", "power bi", "pbi", "dashboard"], ["Report"], "Power BI Report"),
    (["server", "host"], ["Server"], "Server"),
    (["column", "field"], ["Column"], "Column"),
    (["pipeline", "synapse", "alteryx", "etl"], ["DataPipeline"], "Data Pipeline"),
    (["model", "data model", "er studio"], ["DataModel"], "Data Model"),
    (["analyst", "owner", "assigned"], ["Person"], "Data Analyst/Owner"),
    (["process", "business process"], ["BusinessProcess"], "Business Process"),
    (["stage", "value stream"], ["ValueStreamStage"], "Value Stream Stage"),
    (["policy", "classification"], ["Policy"], "Policy"),
    (["business area"], ["BusinessArea"], "Business Area"),
]


def _display_name(props, fallback):
    return props.get("qualifiedName") or props.get("name") or props.get("serverName") or props.get("id") or fallback


def clean_connection_expression(val) -> str:
    """Formats a Power Query (M) connection expression for display."""
    if not val:
        return ""
    if isinstance(val, str):
        val_strip = val.strip()
        if val_strip.startswith("[") or val_strip.startswith("{"):
            try:
                val = ast.literal_eval(val_strip)
            except Exception:
                pass
    if isinstance(val, list):
        if len(val) > 0:
            val = val[0]
        else:
            return ""
    if isinstance(val, dict):
        val = val.get('expression', str(val))
    if isinstance(val, str):
        val = val.replace('\\n', '\n').replace('\\t', '\t')
        val = val.replace('#(lf)', '\n').replace('#(cr)', '\r').replace('#(tab)', '\t')
        val = val.replace("\\'", "'").replace('\\"', '"')
        return val.strip()
    return str(val)


def serialize_graph(recs) -> dict:
    """Every node and relationship in the records, deduplicated by element id."""
    nodes_map = {}
    edges_map = {}

    def process_value(val):
        if isinstance(val, neo4j.graph.Node):
            eid = val.element_id
            nodes_map[eid] = {
                "id": eid,
                "labels": list(val.labels),
                "properties": dict(val.items())
            }
        elif isinstance(val, neo4j.graph.Relationship):
            eid = val.element_id
            edges_map[eid] = {
                "id": eid,
                "source": val.start_node.element_id,
                "target": val.end_node.element_id,
                "type": val.type,
                "properties": dict(val.items())
            }
        elif isinstance(val, neo4j.graph.Path):
            for node in val.nodes:
                process_value(node)
            for rel in val.relationships:
                process_value(rel)
        elif isinstance(val, list):
            for item in val:
                process_value(item)
        elif isinstance(val, dict):
            for item in val.values():
                process_value(item)

    for rec in recs:
        for val in rec.values():
            process_value(val)

    return {
        "nodes": list(nodes_map.values()),
        "edges": list(edges_map.values())
    }


def intent_feedback(question: str, recs) -> str:
    """Self-heal feedback when the records lack the entity type the question
    asks for; empty when they satisfy it."""
    if not recs:
        return ""

    q_lower = (question or "").lower()
    active_intents = [(labels, name) for keywords, labels, name in _INTENTS if any(kw in q_lower for kw in keywords)]
    if not active_intents:
        return ""

    returned_labels = set()

    def collect_labels(val):
        if isinstance(val, neo4j.graph.Node):
            returned_labels.update(val.labels)
        elif isinstance(val, neo4j.graph.Path):
            for node in val.nodes:
                returned_labels.update(node.labels)
        elif isinstance(val, list):
            for item in val:
                collect_labels(item)
        elif isinstance(val, dict):
            for item in val.values():
                collect_labels(item)

    for r in recs:
        for val in r.values():
            collect_labels(val)

    if any(kw in q_lower for kw in ["system", "source system", "operational"]):
        has_operational_or_system = "DataSystem" in returned_labels or "FlatFile" in returned_labels
        if not has_operational_or_system:
            def check_operational_table(val):
                if isinstance(val, neo4j.graph.Node) and "Table" in val.labels:
                    if (val.get("layer") or "").lower() == "operational":
                        return True
                elif isinstance(val, neo4j.graph.Path):
                    for node in val.nodes:
                        if "Table" in node.labels and (node.get("layer") or "").lower() == "operational":
                            return True
                elif isinstance(val, list):
                    return any(check_operational_table(item) for item in val)
                elif isinstance(val, dict):
                    return any(check_operational_table(item) for item in val.values())
                return False

            has_operational_or_system = any(check_operational_table(v) for r in recs for v in r.values())
        if not has_operational_or_system:
            return (
                "The query executed successfully but failed to return any Operational Table, DataSystem, or FlatFile nodes. "
                "You must adjust your Cypher query to correctly traverse and return the Operational sources/systems."
            )

    for labels, name in active_intents:
        if not any(label in returned_labels for label in labels):
            return (
                f"The query executed successfully but failed to return any {name} nodes (expected labels: {labels}). "
                f"You must adjust your Cypher query to properly traverse and return the requested {name} nodes."
            )
    return ""


def _is_medallion_result(recs) -> bool:
    is_medallion = False
    has_non_medallion_node = False

    def check_node(node):
        nonlocal has_non_medallion_node
        if isinstance(node, neo4j.graph.Node):
            if node.labels & _NON_MEDALLION_LABELS:
                has_non_medallion_node = True
            if node.labels & _MEDALLION_LABELS:
                return True
        return False

    for r in recs:
        for v in r.values():
            if check_node(v):
                is_medallion = True
            elif isinstance(v, neo4j.graph.Path):
                if any(check_node(n) for n in v.nodes):
                    is_medallion = True
            elif isinstance(v, list):
                if any(check_node(item) for item in v):
                    is_medallion = True
    return is_medallion and not has_non_medallion_node


def _medallion_rows(recs, ids):
    def process_node(node, row_sets):
        if not isinstance(node, neo4j.graph.Node):
            return
        if node.element_id is not None:
            ids.append(node.element_id)
        labels = node.labels
        props = dict(node.items())
        val = _display_name(props, list(labels)[0] if labels else "Node")
        column = next((col for label, col in _LABEL_COLUMN.items() if label in labels), None)
        if column is None and labels & _TABLE_LABELS:
            column = _LAYER_COLUMN.get((props.get("layer") or "").lower())
        if column:
            row_sets[column].add(val)

    def process_value(val, row_sets):
        if isinstance(val, neo4j.graph.Node):
            process_node(val, row_sets)
        elif isinstance(val, neo4j.graph.Path):
            for node in val.nodes:
                process_node(node, row_sets)
        elif isinstance(val, list):
            for item in val:
                process_value(item, row_sets)

    rows = []
    for r in recs:
        row_sets = {k: set() for k in MEDALLION_COLUMNS}
        for k in r.keys():
            process_value(r.get(k), row_sets)
        rows.append({k: ", ".join(sorted(v)) if v else "-" for k, v in row_sets.items()})
    return rows, dict(MEDALLION_COLUMNS)


def _projected_rows(recs, question, ids):
    raw_rows = []
    key_node_labels = {}
    key_is_relationship = {}
    key_is_path = {}
    key_layers = {}

    for r in recs:
        row_raw = {}
        for k in r.keys():
            v = r.get(k)
            clean_key = k.replace(".", "_")
            row_raw[clean_key] = v

            if isinstance(v, neo4j.graph.Node):
                key_node_labels.setdefault(clean_key, set()).update(v.labels)
                layer_val = v.get("layer")
                if layer_val:
                    key_layers.setdefault(clean_key, set()).add(layer_val)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, neo4j.graph.Node):
                        layer_val = item.get("layer")
                        if layer_val:
                            key_layers.setdefault(clean_key, set()).add(layer_val)
            elif isinstance(v, neo4j.graph.Relationship):
                key_is_relationship[clean_key] = True
            elif isinstance(v, neo4j.graph.Path):
                key_is_path[clean_key] = True

            if getattr(v, "element_id", None) is not None:
                ids.append(v.element_id)

        raw_rows.append(row_raw)

    q_lower = (question or "").lower()
    has_reports_target = any(w in q_lower for w in ["report", "reports", "consuming report", "power bi", "pbi"])
    has_tables_target = any(w in q_lower for w in ["table", "tables", "views", "view"])
    has_owners_target = any(w in q_lower for w in ["owner", "owners", "analyst", "analysts", "data analyst"])

    node_keys = [
        key for key in (raw_rows[0].keys() if raw_rows else [])
        if not key_is_relationship.get(key, False) and not key_is_path.get(key, False)
        and key.lower() not in _EXCLUDED_KEYS
    ]

    if has_owners_target:
        def is_target(key):
            return "Person" in key_node_labels.get(key, set()) or "owner" in key.lower() or "analyst" in key.lower()
    elif has_reports_target:
        def is_target(key):
            return "Report" in key_node_labels.get(key, set()) or "report" in key.lower() or "rpt" in key.lower()
    elif has_tables_target:
        def is_target(key):
            return "Table" in key_node_labels.get(key, set()) or "table" in key.lower()
    else:
        def is_target(key):
            return False
    target_keys = [k for k in node_keys if is_target(k)] + [k for k in node_keys if not is_target(k)]

    if not target_keys and raw_rows:
        target_keys = [k for k in raw_rows[0].keys() if k.lower() not in _EXCLUDED_KEYS]

    def get_sort_index(key: str) -> int:
        k_clean = key.lower()
        return _CONFORMED_ORDER.index(k_clean) if k_clean in _CONFORMED_ORDER else len(_CONFORMED_ORDER)

    target_keys = sorted(target_keys, key=get_sort_index)

    headers = {}
    for key in target_keys:
        layers = key_layers.get(key)
        if layers:
            primary_layer = list(layers)[0].capitalize()
            headers[key] = primary_layer if primary_layer.lower() != "operational" else "Operational Source"
        else:
            headers[key] = _DEFAULT_HEADERS.get(key.lower()) or key.upper().replace("_", " ")

    rows = []
    for raw_row in raw_rows:
        row = {}
        for clean_key in target_keys:
            if clean_key not in raw_row:
                continue
            v = raw_row[clean_key]

            if isinstance(v, (str, list, dict)) and (
                clean_key.lower() in ("expression", "connection_query", "connection query") or
                "expression" in str(v) or "let\n" in str(v) or "#(lf)" in str(v)
            ):
                v = clean_connection_expression(v)

            if isinstance(v, neo4j.graph.Node):
                row[clean_key] = _display_name(dict(v.items()), list(v.labels)[0] if v.labels else "Node")
            elif isinstance(v, neo4j.graph.Relationship):
                row[clean_key] = v.type
            elif isinstance(v, neo4j.graph.Path):
                row[clean_key] = f"Path ({len(v)} hops)"
            elif isinstance(v, list):
                items_str = []
                for item in v:
                    if isinstance(item, neo4j.graph.Node):
                        items_str.append(_display_name(dict(item.items()), ""))
                    elif isinstance(item, neo4j.graph.Relationship):
                        items_str.append(item.type)
                    else:
                        items_str.append(str(item))
                row[clean_key] = ", ".join(filter(None, items_str))
            elif isinstance(v, dict):
                row[clean_key] = _display_name(v, str(v))
            else:
                if isinstance(v, str):
                    v = clean_connection_expression(v)
                row[clean_key] = v
        rows.append(row)
    return rows, headers


def tabulate(recs, question: str = "") -> tuple[list[dict], list[str], dict]:
    """Rows, element ids, and column headers for the Table Grid. Lineage results
    fill the fixed medallion columns; anything else projects its return keys."""
    ids = []
    if _is_medallion_result(recs):
        rows, headers = _medallion_rows(recs, ids)
    else:
        rows, headers = _projected_rows(recs, question, ids)
    return rows, list(dict.fromkeys(ids)), headers
