const API_BASE =
  typeof window !== "undefined"
    ? ((import.meta.env?.VITE_API_URL as string | undefined) ?? "http://localhost:8000")
    : "http://backend:8000";

// ─── Tipos de entidade ────────────────────────────────────────────────────────
export type EntityType =
  | "Story"
  | "Requirement"
  | "TestCase"
  | "BugReport"
  | "Incident"
  | "PostMortem";

// ─── Autenticação ─────────────────────────────────────────────────────────────
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export async function loginUser(payload: LoginRequest): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: payload.username, password: payload.password }),
  });
  if (!response.ok) {
    throw new Error("Credenciais inválidas. Verifique e-mail e senha.");
  }
  return response.json();
}

// ─── Busca semântica ──────────────────────────────────────────────────────────
export interface SearchResult {
  id: string;
  label: EntityType;
  properties: Record<string, unknown>;
  score: number;
}

export interface SemanticSearchResponse {
  results: SearchResult[];
  total: number;
}

export interface SemanticSearchRequest {
  text: string;
  limit_responses?: number;
  filter?: EntityType | null;
}

export async function searchSemantic(
  payload: SemanticSearchRequest,
): Promise<SemanticSearchResponse> {
  const token =
    typeof localStorage !== "undefined" ? localStorage.getItem("dm-token") : null;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}/api/v1/search/semantic`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      request_text: payload.text,
      filter: payload.filter ?? null,
      limit_responses: payload.limit_responses ?? 10,
    }),
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`Erro na busca (${response.status}): ${detail}`);
  }
  return response.json();
}

// ─── Análise de Impacto ───────────────────────────────────────────────────────
export interface ImpactNode {
  id: string;
  label: EntityType;
  properties: Record<string, unknown>;
}

export interface ImpactEdge {
  source: string;
  target: string;
  type: string;
}

export interface ImpactAnalysisResponse {
  nodes: ImpactNode[];
  edges: ImpactEdge[];
}

export async function getImpactAnalysis(
  nodeId: string,
  depth = 3,
): Promise<ImpactAnalysisResponse> {
  const token =
    typeof localStorage !== "undefined" ? localStorage.getItem("dm-token") : null;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(
    `${API_BASE}/api/v1/search/impact-analysis/${encodeURIComponent(nodeId)}?depth=${depth}`,
    { method: "GET", headers },
  );

  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`Erro na análise de impacto (${response.status}): ${detail}`);
  }
  return response.json();
}
