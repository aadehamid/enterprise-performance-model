import axios from 'axios';

export type GraphNodePayload = {
  id: string;
  labels: string[];
  properties: Record<string, any>;
};

export type GraphEdgePayload = {
  id: string;
  source: string;
  target: string;
  type: string;
  properties: Record<string, any>;
};

export type GraphPayload = {
  nodes: GraphNodePayload[];
  edges: GraphEdgePayload[];
};

export type AskSource = {
  listIds: string[];
  rows?: Record<string, any>[];
  graph_data?: GraphPayload;
  headers?: Record<string, string>;
};

export type AskResponse = {
  response?: string;
  cypher?: string;
  error?: string;
  src: AskSource[];
  session_id: string;
};

export type Feedback = 'good' | 'poor';

const ASK_URL =
  import.meta.env.VITE_BACKEND_URL || `${window.location.protocol}//${window.location.hostname}:8000/ask`;
const BASE_URL = ASK_URL.replace(/\/ask\/?$/, '');

export async function postAsk(question: string, sessionId: string, signal: AbortSignal): Promise<AskResponse> {
  const { data } = await axios.post<AskResponse>(ASK_URL, { question, session_id: sessionId }, { signal });
  return data;
}

export async function postFeedback(sessionId: string, feedback: Feedback, comment: string): Promise<void> {
  await axios.post(`${BASE_URL}/api/feedback`, { session_id: sessionId, feedback, comment });
}

export async function postExpand(elementId: string): Promise<GraphPayload> {
  const { data } = await axios.post<GraphPayload>(`${BASE_URL}/api/expand`, { element_id: elementId });
  return data;
}

export const isAbort = axios.isCancel;
