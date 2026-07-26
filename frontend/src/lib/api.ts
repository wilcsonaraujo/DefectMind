// Default por contexto (docker-compose usa o hostname do serviço "backend"
// no SSR, localhost no browser) — mas em qualquer um dos dois casos,
// VITE_API_URL sobrescreve se estiver definida. Antes o branch de SSR
// não tinha como ser configurado por env var de jeito nenhum.
const DEFAULT_API_BASE =
  typeof window !== "undefined" ? "http://localhost:8000" : "http://backend:8000";
const API_BASE = (import.meta.env?.VITE_API_URL as string | undefined) ?? DEFAULT_API_BASE;

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
    // O backend manda a razão real em { detail: "..." } (401 senha errada,
    // 403 conta inativa, etc.) — repassa isso em vez de uma mensagem fixa.
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Falha no login (${response.status})`);
  }
  return response.json();
}

/**
 * Busca os dados reais do usuário logado (nome, e-mail, role).
 * O JWT em si só carrega `sub` (id do usuário) e `role` — nome e
 * e-mail de exibição vêm sempre daqui, nunca do payload do token.
 */
export async function getCurrentUser(): Promise<UserResponse> {
  const response = await fetch(`${API_BASE}/api/v1/auth/me`, {
    method: "GET",
    headers: authHeaders(),
  });
  if (response.status === 401) handleUnauthorized();
  if (!response.ok) {
    throw new Error(`Falha ao carregar usuário atual (${response.status})`);
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
  signal?: AbortSignal,
): Promise<SemanticSearchResponse> {
  const headers = authHeaders();
  const response = await fetch(`${API_BASE}/api/v1/search/semantic`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      request_text: payload.text,
      filter: payload.filter ?? null,
      limit_responses: payload.limit_responses ?? 10,
    }),
    signal,
  });
  if (response.status === 401) handleUnauthorized();
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
  signal?: AbortSignal,
): Promise<ImpactAnalysisResponse> {
  const headers = authHeaders();
  const response = await fetch(
    `${API_BASE}/api/v1/search/impact-analysis/${encodeURIComponent(nodeId)}?depth=${depth}`,
    { method: "GET", headers, signal },
  );
  if (response.status === 401) handleUnauthorized();
  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`Erro na análise de impacto (${response.status}): ${detail}`);
  }
  return response.json();
}

// ─── Estatísticas do Grafo ────────────────────────────────────────────────────
export interface NodeByType {
  Story: number;
  Requirement: number;
  TestCase: number;
  BugReport: number;
  Incident: number;
  PostMortem: number;
}

export interface ConnectedNode {
  id: string;
  label: string;
  title: string | null;
  degree: number;
}

export interface IsolatedNode {
  id: string;
  label: string;
  title: string | null;
}

export interface GraphStatsResponse {
  total_nodes: number;
  total_edges: number;
  nodes_by_type: NodeByType;
  most_connected_nodes: ConnectedNode[];
  isolated_nodes: IsolatedNode[];
  avg_degree: number;
  density: number;
}

export async function getGraphStats(): Promise<GraphStatsResponse> {
  const headers = authHeaders();
  const response = await fetch(`${API_BASE}/api/v1/search/graph-stats`, {
    method: "GET",
    headers,
  });
  if (response.status === 401) handleUnauthorized();
  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`Erro ao carregar estatísticas do grafo (${response.status}): ${detail}`);
  }
  return response.json();
}

// ─── Artefatos ────────────────────────────────────────────────────────────────

function authHeaders(): Record<string, string> {
  const token = typeof localStorage !== "undefined" ? localStorage.getItem("dm-token") : null;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

/**
 * Chamado sempre que um endpoint autenticado devolve 401 — token
 * expirado/inválido/revogado no servidor. Sem isso a UI ficava "logada"
 * indefinidamente e cada chamada virava um 401 silencioso, sem re-login.
 * Não é usado em loginUser (401 ali é "senha errada", não sessão inválida)
 * nem em getHealthStatus (endpoint público, sem auth).
 */
function handleUnauthorized(): void {
  if (typeof localStorage !== "undefined") {
    localStorage.removeItem("dm-token");
  }
  if (typeof window !== "undefined" && window.location.pathname !== "/login") {
    window.location.href = "/login";
  }
}

export interface StoryResponse {
  id: string;
  title: string;
  description: string;
  created_at: string;
}

export interface RequirementResponse {
  id: string;
  title: string;
  description: string;
  priority: "Low" | "Medium" | "High";
  created_at: string;
}

export interface TestCaseResponse {
  id: string;
  title: string;
  steps: string;
  expected_result: string;
  created_at: string;
}

export interface BugReportResponse {
  id: string;
  title: string;
  description: string;
  severity: "Low" | "Medium" | "High" | "Critical";
  created_at: string;
}

export interface IncidentResponse {
  id: string;
  title: string;
  description: string;
  impact: "Low" | "Medium" | "High" | "Critical";
  created_at: string;
}

export interface PostMortemResponse {
  id: string;
  title: string;
  root_cause: string;
  resolution: string;
  lessons_learned: string;
  created_at: string;
}

async function fetchArtifacts<T>(path: string): Promise<T[]> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: authHeaders(),
  });
  if (response.status === 401) handleUnauthorized();
  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`Erro ao carregar artefatos (${response.status}): ${detail}`);
  }
  return response.json();
}

export const getStories = () => fetchArtifacts<StoryResponse>("/api/v1/stories");

export const getRequirements = () => fetchArtifacts<RequirementResponse>("/api/v1/requirements");

export const getTestCases = () => fetchArtifacts<TestCaseResponse>("/api/v1/testcases");

export const getBugReports = () => fetchArtifacts<BugReportResponse>("/api/v1/bugreports");

export const getIncidents = () => fetchArtifacts<IncidentResponse>("/api/v1/incidents");

export const getPostMortems = () => fetchArtifacts<PostMortemResponse>("/api/v1/postmortems");

// ─── Usuários ─────────────────────────────────────────────────────────────────

export interface UserResponse {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
}

export async function getUsers(): Promise<UserResponse[]> {
  const headers = authHeaders();
  const response = await fetch(`${API_BASE}/api/v1/users`, {
    method: "GET",
    headers,
  });
  if (response.status === 401) handleUnauthorized();
  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`Erro ao carregar usuários (${response.status}): ${detail}`);
  }
  return response.json();
}

export interface CreateUserRequest {
  full_name: string;
  email: string;
  password: string;
  role: string;
}

export async function createUser(payload: CreateUserRequest): Promise<UserResponse> {
  const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (response.status === 401) handleUnauthorized();
  if (!response.ok) {
    // 409 (e-mail já cadastrado) manda { detail: "..." } como string;
    // 422 de validação manda uma lista de erros — nesse caso cai no fallback.
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : null;
    throw new Error(detail ?? `Erro ao criar usuário (${response.status})`);
  }
  return response.json();
}

// ─── Health / Status ──────────────────────────────────────────────────────────

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
  database: string;
  neo4j: string;
  timestamp: string;
}

export async function getHealthStatus(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/api/v1/health`, {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error(`Health check falhou (${response.status})`);
  }
  return response.json();
}

// ─── Data Forge ───────────────────────────────────────────────────────────────

export interface GenerateDatasetRequest {
  num_stories: number;
  batch_size: number;
}

export interface GenerateDatasetResult {
  stories?: number;
  requirements?: number;
  testcases?: number;
  bug_reports?: number;
  incidents?: number;
  postmortems?: number;
}

export async function generateDataset(
  payload: GenerateDatasetRequest,
): Promise<GenerateDatasetResult> {
  const headers = authHeaders();
  const response = await fetch(`${API_BASE}/data-forge/generate`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  if (response.status === 401) handleUnauthorized();
  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`Erro ao gerar dataset (${response.status}): ${detail}`);
  }
  return response.json();
}
