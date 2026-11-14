/* src/templates/shared/components/RetrievalInformation.tsx */
import { use, useEffect, useMemo, useRef, useState } from 'react';
import { Box, Typography, Flex, IconButton, LoadingSpinner, Drawer } from '@neo4j-ndl/react';
import './Retrieval.css';
import { MagnifyingGlassResetIcon, FitToScreenIcon } from '@neo4j-ndl/react/icons';
import type NVL from '@neo4j-nvl/base';
import type { HitTargets, Node, Relationship } from '@neo4j-nvl/base';
import { InteractiveNvlWrapper } from '@neo4j-nvl/react';
import type { MouseEventCallbacks } from '@neo4j-nvl/react';
import { ThemeWrapperContext } from '../../../context/ThemeWrapper';
import { postExpand, type GraphPayload } from '../api/backend';
import { layerBadge, legendFor, toNvlGraph } from '../graph/lineageGraph';

// ---------------------------------------------------------------------------
// TanStack Table Imports for High-Performance Tabular Visualization
// ---------------------------------------------------------------------------
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
} from '@tanstack/react-table';

// ---------------------------------------------------------------------------
// Type Definitions
// ---------------------------------------------------------------------------
type RetrievalProps = {
  graphData?: GraphPayload | null;
  rows?: any[];
  model: string;
  timeTaken: number;
  cypher?: string;
  error?: string;
  headers?: Record<string, string>;
};

type Tab = 'graph' | 'table' | 'cypher';

const TABS: { id: Tab; label: string }[] = [
  { id: 'graph', label: 'Graph View' },
  { id: 'table', label: 'Table Grid' },
  { id: 'cypher', label: 'Cypher' },
];

const LEGACY_SCHEMA_MARKERS = ['dwh', 'persistence', 'staging'];

// Conformed header mapping translates technical database keys into readable business terms
const CONFORMED_HEADER_MAP: Record<string, string> = {
  t: 'Table',
  upstream: 'Upstream Table',
  op: 'Operational Source',
  rpl: 'Replica Table',
  ds: 'Data System',
  dm: 'Data Model',
  cdd: 'Capability Data Domain',
  srv: 'Server',
  downstream: 'Downstream Flow',
  df: 'Derivation',
  rpt: 'Report',
  report: 'Report',
  owner: 'Data Analyst',
  ra: 'Role Assignment',
  analystrole: 'Analyst Role',
  uppath: 'Upstream Path',
};

// Pads joined keywords (e.g. REPORTNAME, WORKSPACENAME) so they split into words
const CONFORMED_WORD_PATTERNS = [
  'REPORT', 'WORKSPACE', 'NAME', 'COUNT', 'SYSTEM', 'SERVER', 'FILE',
  'PATH', 'LINEAGE', 'SOURCE', 'TARGET', 'UPSTREAM', 'DOWNSTREAM',
  'ANALYST', 'ROLE', 'TABLE', 'COLUMN', 'SCHEMA', 'DATA', 'FLOW',
].map((word) => [new RegExp(word, 'g'), ` ${word} `] as const);

function appendNew<T extends { id: string }>(existing: T[], incoming: T[]): T[] {
  const seen = new Set(existing.map((item) => item.id));
  const added = incoming.filter((item) => !seen.has(item.id));
  return added.length ? [...existing, ...added] : existing;
}

function conformedHeader(key: string, customHeaders?: Record<string, string>): string {
  const kLower = key.toLowerCase();
  if (customHeaders?.[key] && customHeaders[key].toLowerCase() !== kLower) return customHeaders[key];
  if (customHeaders?.[kLower] && customHeaders[kLower].toLowerCase() !== kLower) return customHeaders[kLower];
  if (CONFORMED_HEADER_MAP[kLower]) return CONFORMED_HEADER_MAP[kLower];

  let upper = key
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/([A-Z])([A-Z][a-z])/g, '$1 $2')
    .replace(/[._-]/g, ' ')
    .toUpperCase();
  for (const [pattern, padded] of CONFORMED_WORD_PATTERNS) upper = upper.replace(pattern, padded);
  return upper.replace(/\s+/g, ' ').trim();
}

// ---------------------------------------------------------------------------
// Cell Renderer for TanStack Table
// ---------------------------------------------------------------------------
// This helper formats physical table values, master data domains, report names,
// and structural legacy properties into modern, color-coded glassmorphic cards.
// ---------------------------------------------------------------------------
const renderCellValue = (val: any) => {
  if (val === null || val === undefined) return <span className="opacity-40">-</span>;
  
  // If the cell contains a primitive string, number, or boolean, return it directly
  if (typeof val !== 'object') return String(val);

  // Extract the display identity safely (catching any circular references in complex Neo4j driver elements)
  let displayVal = '';
  try {
    displayVal = val.qualifiedName || val.name || val.serverName || val.id || JSON.stringify(val);
  } catch {
    displayVal = '[Lineage / Relationship Path]';
  }
  const labels: string = val._labels || '';
  const layer: string = val.layer || '';

  // Determine if this is a pre-standard legacy schema object
  const displayLower = String(displayVal).toLowerCase();
  const isLegacy =
    labels.toLowerCase().includes('legacy') || LEGACY_SCHEMA_MARKERS.some((m) => displayLower.includes(m));

  const badgeStyle = layerBadge(layer) ?? {
    background: 'rgba(255, 255, 255, 0.08)',
    border: '1px solid rgba(255, 255, 255, 0.15)',
    color: '#ffffff',
  };

  return (
    <div style={{
      padding: '8px 12px',
      background: 'rgba(255, 255, 255, 0.03)',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      borderRadius: '8px',
      fontSize: '12px',
      display: 'inline-flex',
      flexDirection: 'column',
      gap: '4px',
      maxWidth: '280px',
    }}>
      <div style={{ fontWeight: 600, overflowWrap: 'anywhere' }}>{displayVal}</div>
      <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
        {labels && (
          <span style={{
            fontSize: '9px',
            padding: '2px 6px',
            borderRadius: '4px',
            background: 'rgba(255, 255, 255, 0.1)',
            color: 'rgba(255, 255, 255, 0.7)',
          }}>
            {labels.split(':').filter(Boolean)[0]}
          </span>
        )}
        
        {layer && (
          <span style={{
            fontSize: '9px',
            padding: '2px 6px',
            borderRadius: '4px',
            ...badgeStyle
          }}>
            {layer}
          </span>
        )}

        {isLegacy && (
          <span style={{
            fontSize: '9px',
            padding: '2px 6px',
            borderRadius: '4px',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid #ef4444',
            color: '#ef4444',
          }}>
            Legacy
          </span>
        )}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Premium TanStack Data Grid View
// ---------------------------------------------------------------------------
function TableView({ data, customHeaders }: { data: any[]; customHeaders?: Record<string, string> }) {
  if (!data || data.length === 0) {
    return (
      <div className='flex items-center justify-center h-full text-center opacity-60' style={{ minHeight: '300px' }}>
        <Typography variant='body-medium'>No records returned for this query.</Typography>
      </div>
    );
  }
  return <DataGrid data={data} customHeaders={customHeaders} />;
}

function DataGrid({ data, customHeaders }: { data: any[]; customHeaders?: Record<string, string> }) {
  // Derive column structure dynamically based on the keys of the returned Cypher record
  const columns = useMemo(
    () =>
      Object.keys(data[0]).map((key) => ({
        accessorKey: key,
        header: conformedHeader(key, customHeaders),
        cell: (info: any) => renderCellValue(info.getValue()),
      })),
    [data, customHeaders],
  );

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div style={{
      flex: 1,
      minHeight: 0,
      width: '100%',
      overflowY: 'auto',
      overflowX: 'auto',
      background: '#070A13', // Solid deep navy-black background for ultimate dark mode contrast
      border: '2px solid #2AADA5', // Distinct border outline matching theme color
      borderRadius: '20px',
      padding: '16px',
      boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.5)',
    }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id} style={{ borderBottom: '3px solid #2AADA5' }}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  style={{
                    padding: '14px 16px',
                    fontSize: '11px',
                    fontWeight: 800,
                    letterSpacing: '0.08em',
                    color: '#38BDF8', // Stunning, highly legible Sky Blue headers
                    textTransform: 'uppercase',
                    background: '#0B0F1E',
                  }}
                >
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row, idx) => (
            <tr
              key={row.id}
              style={{
                borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                background: idx % 2 === 0 ? 'rgba(255, 255, 255, 0.02)' : 'transparent',
                transition: 'background 0.2s',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = idx % 2 === 0 ? 'rgba(255, 255, 255, 0.02)' : 'transparent'; }}
            >
              {row.getVisibleCells().map((cell) => (
                <td
                  key={cell.id}
                  style={{
                    padding: '14px 16px',
                    verticalAlign: 'middle',
                    color: '#FFFFFF', // Pure white, maximum-readability text!
                    fontSize: '13px', // Increased size slightly for easier scanning
                    fontWeight: 500,
                    overflowWrap: 'anywhere',
                  }}
                >
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Dashboard Pane Component
// ---------------------------------------------------------------------------
export default function RetrievalInformation({ graphData, rows, model, timeTaken, cypher, error, headers }: RetrievalProps) {
  const isDark = use(ThemeWrapperContext).colorMode === 'dark';
  const nvl = useRef<NVL | null>(null);
  const [loading, setLoading] = useState(false);
  const [isExpanded, handleIsExpanded] = useState(false);
  const [expandedNode, setExpandedNode] = useState<any>(null);

  // The parent keys this component per answer, so props only seed the initial view.
  const tableOnly = !graphData?.nodes?.length && !!rows?.length;
  const [activeTab, setActiveTab] = useState<Tab>(tableOnly ? 'table' : 'graph');
  const [initialGraph] = useState(() => (tableOnly ? toNvlGraph(null) : toNvlGraph(graphData)));
  const [nodes, setNodes] = useState<Node[]>(initialGraph.nodes);
  const [rels, setRels] = useState<Relationship[]>(initialGraph.rels);

  // Popup context menu position states
  const [contextMenu, setContextMenu] = useState<{
    node: Node; x: number; y: number;
  } | null>(null);

  // Adjust zoom fit when the Details drawer changes size
  useEffect(() => {
    const t = setTimeout(() => {
      try {
        nvl.current?.fit(nodes.map((n) => n.id));
      } catch { /* ignore safe exceptions */ }
    }, 250);
    return () => clearTimeout(t);
  }, [isExpanded, nodes]);

  const fitNodes = () => {
    nvl.current?.fit(nodes.map((n) => n.id));
  };
  const resetZoom = () => {
    nvl.current?.resetZoom();
  };

  const handleExpand = (clickedNode: any) => {
    setExpandedNode(clickedNode);
    handleIsExpanded(true);

    setNodes((prevNodes) =>
      prevNodes.map((node) => ({
        ...node,
        selected: node.id === clickedNode.id
      }))
    );
  };

  // Secure interactive node expansion proxy
  // Instead of compiling Cypher queries on the client side, we send the
  // element_id securely to our backend expand endpoint, keeping all database
  // credentials strictly hidden in backend configuration.
  async function handleNodeExpand(node: Node) {
    if (!node?.id) return;
    setLoading(true);
    try {
      const expanded = toNvlGraph(await postExpand(node.id));

      setNodes((prev) => appendNew(prev, expanded.nodes));
      setRels((prev) => appendNew(prev, expanded.rels));
    } catch (err) {
      console.error('Secure 1-hop node expand failed:', err);
    } finally {
      setLoading(false);
    }
  }

  const mouseEventCallbacks: MouseEventCallbacks = {
    onDrag: true,
    onPan: true,
    onZoomAndPan: true,
    onNodeClick: (node: Node, _hitTargets: HitTargets, evt: MouseEvent) => {
      const containerEl =
        (evt.target as HTMLElement)?.closest('.nvl-canvas-container') ??
        (evt.currentTarget as HTMLElement);
      const rect = containerEl?.getBoundingClientRect();
      setContextMenu({
        node,
        x: rect ? evt.clientX - rect.left : evt.clientX,
        y: rect ? evt.clientY - rect.top : evt.clientY,
      });
    },
    onNodeDoubleClick: (node: Node, _hitTargets, _evt) => {
      setContextMenu(null);
      handleNodeExpand(node);
    },
    onCanvasClick: (_evt) => setContextMenu(null),
  };

  const menuItemStyle = {
    display: 'block',
    width: '100%',
    textAlign: 'left' as const,
    padding: '8px 12px',
    background: 'transparent',
    border: 'none',
    color: 'var(--theme-color-neutral-text-default)',
    fontSize: '12px',
    cursor: 'pointer' as const,
    borderRadius: '4px',
    transition: 'background 0.2s',
  };

  const activeLegendItems = legendFor(nodes);

  return (
    <Box className='bg-neutral-bg-weak border! border-neutral-border-weak rounded-2xl p-4' style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      
      {/* ---------------------------------------------------------------------
          Glassmorphic Switch Header Container
          --------------------------------------------------------------------- */}
      <Flex flexDirection='row' justifyContent='space-between' alignItems='center' className='mb-4' style={{ width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Box className='flex flex-col'>
            <Typography variant='title-4' style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 700, margin: 0 }}>Conversational Search & Semantic Dashboard</Typography>
            <Typography variant='body-small' className='italic opacity-80' style={{ margin: 0 }}>
              Parsed by <span className='font-bold italic'>{model}</span> in {timeTaken / 1000}s
            </Typography>
          </Box>
        </div>
        
        {/* Toggle switch with premium glassmorphism */}
        <div style={{
          display: 'inline-flex',
          background: isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.05)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: isDark ? '1px solid rgba(255, 255, 255, 0.12)' : '1px solid rgba(0, 0, 0, 0.12)',
          borderRadius: '30px',
          padding: '4px',
          boxShadow: isDark ? '0 8px 32px 0 rgba(0, 0, 0, 0.3)' : '0 8px 32px 0 rgba(0, 0, 0, 0.08)',
        }}>
          {TABS.map(({ id, label }) => {
            const isActive = activeTab === id;
            return (
              <button
                key={id}
                type='button'
                aria-pressed={isActive}
                onClick={() => setActiveTab(id)}
                className='focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#38BDF8]'
                style={{
                  padding: '6px 14px',
                  borderRadius: '25px',
                  border: 'none',
                  background: isActive ? 'linear-gradient(135deg, #2AADA5, #0A6190)' : 'transparent',
                  color: isActive ? '#FFFFFF' : isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                  fontWeight: 600,
                  fontSize: '12px',
                  cursor: 'pointer',
                  transition: 'color 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: isActive ? '0 4px 15px rgba(42, 173, 165, 0.35)' : 'none',
                }}
              >
                {label}
              </button>
            );
          })}
        </div>
      </Flex>

      {/* ---------------------------------------------------------------------
          Dashboard Content Window: Switches between Graph, Table, and Cypher
          --------------------------------------------------------------------- */}
      <div className='button-container' style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, height: 'calc(100% - 85px)', overflow: 'hidden' }}>
        {activeTab === 'table' ? (
          <TableView data={rows || []} customHeaders={headers} />
        ) : activeTab === 'cypher' ? (
          <div style={{
            borderRadius: '25px',
            border: '2px solid #2AADA5',
            width: '100%',
            height: '100%',
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            background: '#070A13', // Matches beautiful dark mode Cypher terminal
            boxShadow: `2px -2px 10px rgba(0, 0, 0, 0.2)`,
            overflow: 'hidden',
          }}>
            <div className='px-6 py-4 border-b! border-[rgba(255,255,255,0.08)] flex justify-between items-center bg-[#0B0F1E]'>
              <Typography variant='subheading-large' style={{ color: '#38BDF8', fontWeight: 700, margin: 0 }}>
                Generated Cypher Query
              </Typography>
              {error && (
                <span className='text-xs px-2.5 py-1 rounded bg-[rgba(239,68,68,0.15)] text-[#ef4444] border! border-[#ef4444] font-mono'>
                  Query Error
                </span>
              )}
            </div>
            <div className='flex-1 overflow-auto p-6'>
              <pre
                style={{
                  color: '#34D399', // Brilliant emerald green
                  textShadow: '0 0 3px rgba(52, 211, 153, 0.2)',
                  fontFamily: "Monaco, Consolas, 'Andale Mono', 'Ubuntu Mono', monospace",
                  fontSize: '13px',
                  lineHeight: '1.6',
                }}
                className='whitespace-pre-wrap m-0'
              >
                {cypher || 'Ask a question — the generated Cypher appears here.'}
              </pre>
              {error && (
                <div className='mt-4 p-4 text-xs rounded-xl bg-[rgba(239,68,68,0.1)] border! border-[rgba(239,68,68,0.2)] text-[#FF9B9B] whitespace-pre-wrap font-mono'>
                  {error}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div
            style={{
              borderRadius: '25px',
              border: '2px solid #2AADA5',
              width: '100%',
              height: '100%',
              flexGrow: 1,
              display: 'flex',
              flexDirection: 'column',
              background: 'var(--theme-color-primary-bg-weak)',
              boxShadow: `2px -2px 10px rgba(0, 0, 0, 0.2)`,
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {/* Graph Legend */}
            {activeLegendItems.length > 0 && (
              <div style={{
                position: 'absolute',
                top: '16px',
                left: isExpanded ? 'calc(33% + 24px)' : '16px',
                zIndex: 100,
                display: 'flex',
                flexWrap: 'wrap',
                gap: '12px',
                maxWidth: isExpanded ? 'calc(67% - 80px)' : '75%',
                background: 'rgba(7, 10, 19, 0.85)',
                backdropFilter: 'blur(12px)',
                WebkitBackdropFilter: 'blur(12px)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '12px',
                padding: '10px 14px',
                boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.4)',
                transition: 'all 0.3s ease-in-out',
              }}>
                {activeLegendItems.map(item => (
                  <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{
                      width: '10px',
                      height: '10px',
                      borderRadius: '50%',
                      backgroundColor: item.color,
                      boxShadow: `0 0 8px ${item.color}`,
                      display: 'inline-block',
                    }} />
                    <span style={{ fontSize: '10px', fontWeight: 700, color: 'rgba(255, 255, 255, 0.85)', letterSpacing: '0.03em' }}>{item.label}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Viewport Control Buttons */}
            <Flex
              flexDirection='row'
              className='flex flex-row p-6'
              style={{
                position: 'absolute',
                top: 0,
                right: 0,
                zIndex: 1000,
              }}
            >
              <IconButton className='n-size-token-7' description='Fit to screen' onClick={fitNodes}>
                <FitToScreenIcon />
              </IconButton>
              <IconButton className='n-size-token-7' description='Reset zoom' onClick={resetZoom}>
                <MagnifyingGlassResetIcon />
              </IconButton>
            </Flex>

            {loading && (
              <LoadingSpinner
                size='large'
                style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  zIndex: 1001,
                }}
              />
            )}

            {/* Interactive Graph Canvas Wrapper */}
            <InteractiveNvlWrapper
              className='rounded-5xl overflow-hidden nvl-canvas-container'
              ref={nvl}
              nodes={nodes}
              rels={rels}
              mouseEventCallbacks={mouseEventCallbacks}
              style={{ width: '100%', height: '100%', minHeight: '520px', flexGrow: 1 }}
              nvlOptions={{
                initialZoom: 0,
                layout: 'd3Force',
                relationshipThreshold: 1,
                styling: { selectedBorderColor: isDark ? '#F5F5F5' : '#1A1B1D' },
              }}
            />

            {/* Interactive 1-Hop Expansion & details Popup Context Menu */}
            {contextMenu && (
              <div
                role='menu'
                onClick={(e) => e.stopPropagation()}
                onKeyDown={(e) => { if (e.key === 'Escape') setContextMenu(null); }}
                style={{
                  position: 'absolute',
                  left: Math.min(contextMenu.x, window.innerWidth - 200),
                  top: Math.min(contextMenu.y, window.innerHeight - 200),
                  transform: 'translate(8px, 8px)',
                  zIndex: 2000,
                  background: 'var(--theme-color-neutral-bg-weak)',
                  border: '1px solid var(--theme-color-neutral-border-strong)',
                  borderRadius: '8px',
                  boxShadow: '0 4px 14px rgba(0,0,0,0.45)',
                  padding: '4px',
                  minWidth: '130px',
                }}
              >
                <button
                  type='button'
                  role='menuitem'
                  style={menuItemStyle}
                  onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--app-overlay)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
                  onClick={() => {
                    const n = contextMenu.node;
                    setContextMenu(null);
                    handleExpand(n);
                  }}
                >
                  Show Details
                </button>
                <button
                  type='button'
                  role='menuitem'
                  style={menuItemStyle}
                  onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--app-overlay)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
                  onClick={() => {
                    const n = contextMenu.node;
                    setContextMenu(null);
                    handleNodeExpand(n);
                  }}
                >
                  Expand 1-Hop
                </button>
              </div>
            )}

            {/* -----------------------------------------------------------------
                Details Panel Drawer
                ----------------------------------------------------------------- */}
            <Drawer
              ariaLabel='Node details'
              isCloseable={false}
              isExpanded={isExpanded}
              position="left"
              type="overlay"
              style={{ zIndex: 2000 }}
              className="rounded-tl-5xl rounded-bl-5xl !w-[33%] !min-w-[260px] !max-w-[520px]"
              onExpandedChange={() => {
                handleIsExpanded(false);
              }}
            >
              <Drawer.Header style={{ position: 'relative' }}>
                <button
                  type="button"
                  aria-label="Close details"
                  onClick={() => handleIsExpanded(false)}
                  style={{
                    position: 'absolute',
                    top: '16px',
                    right: '16px',
                    background: 'transparent',
                    border: 'none',
                    color: isDark ? '#ffffff' : '#000000',
                    fontSize: '20px',
                    cursor: 'pointer',
                    opacity: 0.6,
                    transition: 'opacity 0.2s',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.opacity = '1'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.opacity = '0.6'; }}
                >
                  ✕
                </button>
                <div>
                  <Typography variant='body-medium'>Node Details</Typography>
                </div>
                <div>
                  <Typography variant='subheading-large'>
                    {expandedNode?.properties?.__labels?.[0] ?? 'Node'}
                  </Typography>
                </div>
              </Drawer.Header>
              <Drawer.Body className="pl-5 overflow-y-auto max-h-[calc(100vh-120px)]">
                {expandedNode?.properties && Object.keys(expandedNode.properties).length > 0 && (
                  <div className="mb-4">
                    <figcaption className="caption-top text-xs mb-2 opacity-60">
                      Properties
                    </figcaption>
                    <table className="text-xs w-full" style={{ borderCollapse: 'collapse' }}>
                      <tbody>
                        {Object.entries(expandedNode.properties)
                          .filter(([k]) => !['image_base64', 'embedding', 'text_as_html', '__labels'].includes(k))
                          .map(([k, v]) => (
                            <tr key={k} style={{ borderBottom: '1px solid var(--app-border-subtle)' }}>
                              <td className="pr-3 py-1 align-top font-bold" style={{ whiteSpace: 'nowrap', opacity: 0.7 }}>{k}</td>
                              <td className="py-1" style={{ overflowWrap: 'anywhere' }}>
                                {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </Drawer.Body>
            </Drawer>
          </div>
        )}
      </div>
    </Box>
  );
}
