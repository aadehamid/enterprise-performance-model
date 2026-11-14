import type { Node, Relationship } from '@neo4j-nvl/base';
import type { GraphPayload } from '../api/backend';

export type Swatch = { label: string; color: string };

type LayerSwatch = Swatch & { border: string; tint: string };

const LAYERS: Record<string, LayerSwatch> = {
  operational: { label: 'Operational', color: '#FF8E6A', border: '#FF8E6A', tint: 'rgba(255, 142, 106, 0.15)' },
  replica: { label: 'Replica', color: '#2AADA5', border: '#2AADA5', tint: 'rgba(42, 173, 165, 0.15)' },
  silver: { label: 'Silver', color: '#88C0D0', border: '#0A6190', tint: 'rgba(10, 97, 144, 0.15)' },
  gold: { label: 'Gold', color: '#FFC300', border: '#FFC300', tint: 'rgba(255, 195, 0, 0.15)' },
  semantic: { label: 'Semantic', color: '#B38EFF', border: '#B38EFF', tint: 'rgba(179, 142, 255, 0.15)' },
};

const LABELS: Record<string, Swatch> = {
  Server: { label: 'Server', color: '#7E84F7' },
  DataSystem: { label: 'Data System', color: '#5E81AC' },
  Report: { label: 'Report', color: '#E15D7E' },
  MasterDataDomain: { label: 'Master Data', color: '#D08770' },
  Person: { label: 'Data Analyst', color: '#BF616A' },
  CapabilityDataDomain: { label: 'Capability Domain', color: '#EBCB8B' },
  FlatFile: { label: 'Flat File', color: '#4C566A' },
};

const LEGEND: Swatch[] = [
  LABELS.Server,
  LABELS.DataSystem,
  LAYERS.operational,
  LAYERS.replica,
  LAYERS.silver,
  LAYERS.gold,
  LAYERS.semantic,
  LABELS.Report,
  LABELS.MasterDataDomain,
  LABELS.Person,
  LABELS.CapabilityDataDomain,
  LABELS.FlatFile,
];

const TABLE_LABELS = new Set(['Table', 'Dimension', 'Fact', 'View']);
const UNKNOWN_LAYER_COLOR = '#A3BE8C';
const DEFAULT_COLOR = '#D8DEE9';

function layerOf(layer: unknown): LayerSwatch | undefined {
  return LAYERS[String(layer ?? '').toLowerCase()];
}

function nodeColor(labels: string[], layer: unknown): string {
  const firstLabel = labels[0] || 'Node';
  if (TABLE_LABELS.has(firstLabel) || labels.includes('Legacy')) {
    return layerOf(layer)?.color ?? UNKNOWN_LAYER_COLOR;
  }
  return LABELS[firstLabel]?.color ?? DEFAULT_COLOR;
}

export function layerBadge(layer: string): { background: string; border: string; color: string } | undefined {
  const swatch = layerOf(layer);
  return swatch && { background: swatch.tint, border: `1px solid ${swatch.border}`, color: swatch.color };
}

export type LineageNode = Node & { properties: Record<string, any> };
export type LineageRel = Relationship & { properties: Record<string, any> };

export function toNvlGraph(payload: GraphPayload | null | undefined): { nodes: LineageNode[]; rels: LineageRel[] } {
  if (!payload?.nodes) return { nodes: [], rels: [] };

  const nodes = payload.nodes.map((node): LineageNode => {
    const props = node.properties || {};
    const labels = node.labels || [];
    const caption = props.qualifiedName || props.name || props.serverName || props.id || labels[0] || 'Node';
    return {
      id: node.id.toString(),
      color: nodeColor(labels, props.layer),
      captions: [{ value: String(caption) }],
      properties: { ...props, __labels: labels },
    };
  });

  const rels = (payload.edges || []).map(
    (edge): LineageRel => ({
      id: edge.id.toString(),
      from: edge.source.toString(),
      to: edge.target.toString(),
      captions: [{ value: edge.type ? edge.type.toString() : '' }],
      properties: edge.properties,
    }),
  );

  return { nodes, rels };
}

export function legendFor(nodes: Node[]): Swatch[] {
  const shown = new Set(nodes.map((n) => n.color));
  return LEGEND.filter((item) => shown.has(item.color));
}
