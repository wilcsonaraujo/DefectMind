export type ArtifactType =
  | "Story"
  | "Requirement"
  | "Test Case"
  | "Bug"
  | "Incident"
  | "Post-Mortem";

export const artifactTypeColors: Record<ArtifactType, string> = {
  Story: "bg-chart-1/15 text-chart-1 border-chart-1/30",
  Requirement: "bg-chart-5/15 text-chart-5 border-chart-5/30",
  "Test Case": "bg-chart-2/15 text-chart-2 border-chart-2/30",
  Bug: "bg-destructive/15 text-destructive border-destructive/30",
  Incident: "bg-warning/15 text-warning border-warning/30",
  "Post-Mortem": "bg-accent-foreground/10 text-muted-foreground border-border",
};

export const dashboardStats = [
  { type: "Story" as ArtifactType, label: "Stories", value: 512, change: "+12 esta semana" },
  { type: "Requirement" as ArtifactType, label: "Requisitos", value: 1842, change: "+28 esta semana" },
  { type: "Test Case" as ArtifactType, label: "Test Cases", value: 4562, change: "+76 esta semana" },
  { type: "Bug" as ArtifactType, label: "Bugs", value: 2731, change: "+43 esta semana" },
  { type: "Incident" as ArtifactType, label: "Incidentes", value: 342, change: "+5 esta semana" },
  { type: "Post-Mortem" as ArtifactType, label: "Post-mortems", value: 215, change: "+3 esta semana" },
];

export const graphDonut = [
  { name: "Stories", value: 512, color: "var(--chart-1)" },
  { name: "Requisitos", value: 1842, color: "var(--chart-2)" },
  { name: "Test Cases", value: 4562, color: "var(--chart-3)" },
  { name: "Bugs", value: 2731, color: "var(--chart-4)" },
  { name: "Incidentes", value: 342, color: "var(--chart-5)" },
  { name: "Post-mortems", value: 215, color: "oklch(0.7 0.17 330)" },
];

export const recentSearches = [
  { query: "falhas de autenticação por timeout", tag: "Bug" as ArtifactType, when: "Hoje" },
  { query: "erros ao processar pagamento pix", tag: "Incident" as ArtifactType, when: "Ontem" },
  { query: "saldo negativo permitido", tag: "Bug" as ArtifactType, when: "2 dias atrás" },
  { query: "estorno não processado", tag: "Incident" as ArtifactType, when: "3 dias atrás" },
];

export const recentAnalyses = [
  { story: "STORY-1024 - Transferência entre contas", risk: "Alto risco", when: "Hoje" },
  { story: "STORY-0891 - Pagamento de boleto", risk: "Médio risco", when: "Ontem" },
  { story: "STORY-0733 - Cadastro de beneficiário", risk: "Baixo risco", when: "2 dias atrás" },
];

export const riskBadgeColor: Record<string, string> = {
  "Alto risco": "bg-destructive/15 text-destructive border-destructive/30",
  "Médio risco": "bg-warning/15 text-warning border-warning/30",
  "Baixo risco": "bg-success/15 text-success border-success/30",
};

export const recentActivity = [
  { id: 1, kind: "success", title: "Dataset bancário gerado com sucesso", desc: "512 Stories, 1.842 Requisitos, 4.562 Test Cases…", time: "Hoje 10:30" },
  { id: 2, kind: "warning", title: "Novo incidente criado: INC-342", desc: "Falha em lote de transferências via API", time: "Hoje 09:15" },
  { id: 3, kind: "bug", title: "Bug relacionado encontrado: BUG-2189", desc: "Timeout ao consultar saldo", time: "Ontem 16:45" },
  { id: 4, kind: "impact", title: "Análise de impacto concluída: STORY-1024", desc: "25 impactos encontrados", time: "Ontem 14:22" },
];

export const topBugs = [
  { id: "BUG-2189", title: "Timeout ao consultar saldo", severity: "Crítica", count: 45 },
  { id: "BUG-2077", title: "Saldo negativo permitido", severity: "Crítica", count: 38 },
  { id: "BUG-1983", title: "Falha ao processar PIX", severity: "Alta", count: 29 },
  { id: "BUG-1765", title: "Erro ao validar limite diário", severity: "Alta", count: 24 },
  { id: "BUG-1622", title: "Estorno não processado", severity: "Média", count: 19 },
];

export const severityColor: Record<string, string> = {
  Crítica: "bg-destructive/15 text-destructive border-destructive/30",
  Alta: "bg-warning/15 text-warning border-warning/30",
  Média: "bg-chart-5/15 text-chart-5 border-chart-5/30",
  Baixa: "bg-muted text-muted-foreground border-border",
  High: "bg-warning/15 text-warning border-warning/30",
  Critical: "bg-destructive/15 text-destructive border-destructive/30",
  Medium: "bg-chart-5/15 text-chart-5 border-chart-5/30",
};

export const graphSummary = [
  { label: "Total Nodes", value: "15,327" },
  { label: "Relationships", value: "48,912" },
  { label: "Embeddings", value: "13,940" },
  { label: "Clusters", value: "164" },
];

export const searchHistory = [
  "checkout fails on safari",
  "timeout payment gateway",
  "duplicate user registration",
  "graph rendering performance",
];

export const searchResults = [
  { type: "Bug" as ArtifactType, id: "BUG-2189", title: "Timeout ao consultar saldo", score: 0.94, snippet: "Usuários relatam falha de autenticação por timeout ao consultar o saldo." },
  { type: "Incident" as ArtifactType, id: "INC-342", title: "Falha em lote de transferências via API", score: 0.89, snippet: "Timeouts no gateway causaram transações falhas por 23 minutos." },
  { type: "Story" as ArtifactType, id: "STORY-1024", title: "Transferência entre contas", score: 0.83, snippet: "Como cliente quero transferir entre contas de forma confiável." },
  { type: "Test Case" as ArtifactType, id: "TC-5521", title: "Validar reautenticação após expiração de token", score: 0.78, snippet: "Garantir que a sessão expirada é renovada silenciosamente." },
  { type: "Post-Mortem" as ArtifactType, id: "PM-09", title: "Retrospectiva de timeout no gateway", score: 0.71, snippet: "Causa raiz: esgotamento do pool de conexões sob pico de carga." },
];

export const stories = [
  { id: "STORY-1024", title: "Transferência entre contas" },
  { id: "STORY-0891", title: "Pagamento de boleto" },
  { id: "STORY-0733", title: "Cadastro de beneficiário" },
  { id: "STORY-0512", title: "Limite diário de transferência" },
];

export const relatedBugs = [
  { id: "BUG-2189", title: "Timeout ao consultar saldo", severity: "Alta" },
  { id: "BUG-2077", title: "Saldo negativo permitido", severity: "Crítica" },
  { id: "BUG-1983", title: "Falha ao processar PIX", severity: "Média" },
];

export const relatedIncidents = [
  { id: "INC-342", title: "Falha em lote de transferências via API", impact: "Alta" },
  { id: "INC-318", title: "Latência elevada na API de pagamentos", impact: "Média" },
];

export const riskAreas = [
  { area: "Gateway de Pagamento", level: 86 },
  { area: "Gestão de Sessão", level: 64 },
  { area: "Transferências", level: 47 },
  { area: "Exportação de Dados", level: 28 },
];

export const artifacts = [
  { type: "Bug" as ArtifactType, id: "BUG-2189", name: "Timeout ao consultar saldo", date: "18/06/2026", relationships: 7 },
  { type: "Story" as ArtifactType, id: "STORY-1024", name: "Transferência entre contas", date: "17/06/2026", relationships: 12 },
  { type: "Incident" as ArtifactType, id: "INC-342", name: "Falha em lote de transferências via API", date: "16/06/2026", relationships: 5 },
  { type: "Test Case" as ArtifactType, id: "TC-5521", name: "Validar reautenticação após expiração de token", date: "16/06/2026", relationships: 3 },
  { type: "Requirement" as ArtifactType, id: "REQ-0912", name: "Sessão deve renovar token automaticamente", date: "15/06/2026", relationships: 9 },
  { type: "Post-Mortem" as ArtifactType, id: "PM-09", name: "Retrospectiva de timeout no gateway", date: "14/06/2026", relationships: 6 },
  { type: "Bug" as ArtifactType, id: "BUG-2077", name: "Saldo negativo permitido", date: "13/06/2026", relationships: 4 },
  { type: "Story" as ArtifactType, id: "STORY-0891", name: "Pagamento de boleto", date: "12/06/2026", relationships: 14 },
];

export const users = [
  { name: "Mariana Alves", email: "mariana@defectmind.dev", role: "Admin", team: "QA Core", status: "Ativo" },
  { name: "Carlos Mendes", email: "carlos@defectmind.dev", role: "Líder de QA", team: "Pagamentos", status: "Ativo" },
  { name: "Júlia Faro", email: "julia@defectmind.dev", role: "Engenheira", team: "Plataforma", status: "Ativo" },
  { name: "Pedro Lima", email: "pedro@defectmind.dev", role: "Analista", team: "Confiabilidade", status: "Convidado" },
  { name: "Sofia Ramos", email: "sofia@defectmind.dev", role: "Visualizador", team: "Produto", status: "Inativo" },
];

export type GraphNode = {
  id: string;
  label: string;
  type: ArtifactType;
  x: number;
  y: number;
};

export const graphNodes: GraphNode[] = [
  { id: "n1", label: "STORY-118", type: "Story", x: 50, y: 18 },
  { id: "n2", label: "REQ-0912", type: "Requirement", x: 20, y: 40 },
  { id: "n3", label: "TC-5521", type: "Test Case", x: 80, y: 40 },
  { id: "n4", label: "BUG-2381", type: "Bug", x: 30, y: 70 },
  { id: "n5", label: "INC-0042", type: "Incident", x: 70, y: 72 },
  { id: "n6", label: "PM-09", type: "Post-Mortem", x: 50, y: 92 },
];

export const graphEdges: [string, string][] = [
  ["n1", "n2"],
  ["n1", "n3"],
  ["n2", "n4"],
  ["n3", "n4"],
  ["n4", "n5"],
  ["n5", "n6"],
  ["n1", "n5"],
];