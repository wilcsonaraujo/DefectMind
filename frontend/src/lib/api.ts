const API_BASE =
  typeof window !== "undefined"
    ? ((import.meta.env?.VITE_API_URL as string | undefined) ?? "http://localhost:8000")
    : "http://backend:8000";

export type EntityType =
  | "Story"
  | "Requirement"
  | "TestCase"
  | "BugReport"
  | "Incident"
  | "PostMortem";

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
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`Erro na busca (${response.status}): ${detail}`);
  }

  return response.json();
}