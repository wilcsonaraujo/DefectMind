import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

export type Lang = "pt" | "en";

type Dict = Record<string, { pt: string; en: string }>;

const dict: Dict = {
  // Layout / nav
  "tagline": { pt: "Inteligência para QA", en: "QA Intelligence" },
  "nav.navigation": { pt: "Navegação", en: "Navigation" },
  "nav.config": { pt: "Configurações", en: "Settings" },
  "nav.dashboard": { pt: "Dashboard", en: "Dashboard" },
  "nav.dashboard.sub": { pt: "Visão geral", en: "Overview" },
  "nav.search": { pt: "Buscar", en: "Search" },
  "nav.search.sub": { pt: "Busca semântica", en: "Semantic search" },
  "nav.impact": { pt: "Análise de Impacto", en: "Impact Analysis" },
  "nav.impact.sub": { pt: "Ver relações e riscos", en: "View relations and risks" },
  "nav.graph": { pt: "Explorador de Grafo", en: "Graph Explorer" },
  "nav.graph.sub": { pt: "Visualizar conexões", en: "Visualize connections" },
  "nav.dataForge": { pt: "Data Forge", en: "Data Forge" },
  "nav.dataForge.sub": { pt: "Gerar dados sintéticos", en: "Generate synthetic data" },
  "nav.artifacts": { pt: "Artefatos", en: "Artifacts" },
  "nav.artifacts.sub": { pt: "Gerenciar entidades", en: "Manage entities" },
  "nav.users": { pt: "Usuários", en: "Users" },
  "nav.settings": { pt: "Configurações", en: "Settings" },
  "nav.environments": { pt: "Ambientes", en: "Environments" },
  "status.environment": { pt: "Ambiente", en: "Environment" },
  "status.version": { pt: "Versão", en: "Version" },
  "status.neo4j": { pt: "Neo4j", en: "Neo4j" },
  "status.connected": { pt: "Conectado", en: "Connected" },
  "lang.label": { pt: "Idioma", en: "Language" },

  // Dashboard
  "dash.title": { pt: "Olá, Admin 👋", en: "Hello, Admin 👋" },
  "dash.subtitle": { pt: "Bem-vindo ao DefectMind. Use a busca ou explore os dados gerados para obter insights.", en: "Welcome to DefectMind. Use search or explore the generated data to gain insights." },
  "dash.generateDataset": { pt: "Gerar dataset", en: "Generate dataset" },
  "dash.semanticSearch": { pt: "Busca Semântica", en: "Semantic Search" },
  "dash.semanticSearch.desc": { pt: "Encontre artefatos relacionados usando linguagem natural", en: "Find related artifacts using natural language" },
  "dash.searchPlaceholder": { pt: "Ex: falhas de autenticação por timeout", en: "Ex: authentication failures by timeout" },
  "dash.search": { pt: "Buscar", en: "Search" },
  "dash.recentSearches": { pt: "Buscas recentes", en: "Recent searches" },
  "dash.viewAllSearches": { pt: "Ver todas as buscas", en: "View all searches" },
  "dash.impact": { pt: "Análise de Impacto", en: "Impact Analysis" },
  "dash.impact.desc": { pt: "Selecione uma Story para ver impactos e relações", en: "Select a Story to view impacts and relations" },
  "dash.selectStory": { pt: "Selecione uma Story", en: "Select a Story" },
  "dash.analyze": { pt: "Analisar", en: "Analyze" },
  "dash.recentAnalyses": { pt: "Análises recentes", en: "Recent analyses" },
  "dash.viewAllAnalyses": { pt: "Ver todas as análises", en: "View all analyses" },
  "dash.graphSummary": { pt: "Resumo do Grafo", en: "Graph Summary" },
  "dash.graphSummary.desc": { pt: "Total de nós no grafo", en: "Total nodes in the graph" },
  "dash.total": { pt: "Total", en: "Total" },
  "dash.exploreFullGraph": { pt: "Explorar grafo completo", en: "Explore full graph" },
  "dash.recentActivity": { pt: "Atividades Recentes", en: "Recent Activity" },
  "dash.viewAllActivity": { pt: "Ver todas as atividades", en: "View all activity" },
  "dash.topBugs": { pt: "Top Bugs por Severidade", en: "Top Bugs by Severity" },
  "dash.viewAllBugs": { pt: "Ver todos os bugs", en: "View all bugs" },
  "dash.quickActions": { pt: "Ações Rápidas", en: "Quick Actions" },
  "qa.newDataset": { pt: "Gerar novo dataset", en: "Generate new dataset" },
  "qa.newDataset.desc": { pt: "Criar dados sintéticos relacionados", en: "Create related synthetic data" },
  "qa.exploreGraph": { pt: "Explorar grafo", en: "Explore graph" },
  "qa.exploreGraph.desc": { pt: "Visualizar conexões entre artefatos", en: "Visualize connections between artifacts" },
  "qa.newSearch": { pt: "Nova busca", en: "New search" },
  "qa.newSearch.desc": { pt: "Fazer uma busca semântica", en: "Run a semantic search" },
  "qa.newImpact": { pt: "Nova análise de impacto", en: "New impact analysis" },
  "qa.newImpact.desc": { pt: "Analisar impactos de uma Story", en: "Analyze impacts of a Story" },

  // Search page
  "search.title": { pt: "Busca Semântica", en: "Semantic Search" },
  "search.subtitle": { pt: "Encontre artefatos relacionados por significado, não apenas palavras-chave", en: "Find related artifacts by meaning, not just keywords" },
  "search.placeholder": { pt: "Descreva o problema em linguagem natural…", en: "Describe the problem in natural language…" },
  "search.button": { pt: "Buscar", en: "Search" },
  "search.loading": { pt: "Buscando...", en: "Searching..." },
  "search.filterPlaceholder": { pt: "Filtrar tipo", en: "Filter type" },
  "search.noResults": { pt: "Nenhum resultado encontrado", en: "No results found" },
  "search.error": { pt: "Erro ao buscar", en: "Search error" },
  "search.resultsSuffix": { pt: "resultados · ordenados por similaridade", en: "results · sorted by similarity" },
  "search.history": { pt: "Histórico de buscas", en: "Search history" },

  // Impact page
  "impact.title": { pt: "Análise de Impacto", en: "Impact Analysis" },
  "impact.subtitle": { pt: "Entenda o raio de impacto de uma story no seu grafo", en: "Understand the blast radius of a story across your graph" },
  "impact.selectStory": { pt: "Selecione uma Story", en: "Select a Story" },
  "impact.bugs": { pt: "Bugs", en: "Bugs" },
  "impact.incidents": { pt: "Incidentes", en: "Incidents" },
  "impact.riskAreas": { pt: "Áreas de Risco", en: "Risk Areas" },
  "impact.relatedBugs": { pt: "Bugs Relacionados", en: "Related Bugs" },
  "impact.relatedIncidents": { pt: "Incidentes Relacionados", en: "Related Incidents" },
  "impact.impactPrefix": { pt: "impacto", en: "impact" },

  // Graph page
  "graph.title": { pt: "Explorador de Grafo", en: "Graph Explorer" },
  "graph.subtitle": { pt: "Visualização interativa das relações entre artefatos (simulado)", en: "Interactive visualization of artifact relations (simulated)" },
  "graph.legend": { pt: "Legenda", en: "Legend" },
  "graph.nodeDetails": { pt: "Detalhes do Nó", en: "Node Details" },
  "graph.relations": { pt: "relações no grafo", en: "relations in the graph" },
  "graph.clickNode": { pt: "Clique em um nó para inspecioná-lo.", en: "Click a node to inspect it." },

  // Data Forge
  "forge.title": { pt: "Data Forge", en: "Data Forge" },
  "forge.subtitle": { pt: "Gere datasets de QA sintéticos e totalmente relacionados", en: "Generate fully related synthetic QA datasets" },
  "forge.config": { pt: "Configuração do Dataset", en: "Dataset Configuration" },
  "forge.quantityOf": { pt: "Quantidade de", en: "Quantity of" },
  "forge.generate": { pt: "Generate Dataset", en: "Generate Dataset" },
  "forge.generating": { pt: "Gerando…", en: "Generating…" },
  "forge.progressTitle": { pt: "Progresso da Geração", en: "Generation Progress" },
  "forge.progress": { pt: "Progresso", en: "Progress" },
  "forge.successSuffix": { pt: "artefatos gerados com sucesso.", en: "artifacts generated successfully." },
  "forge.forging": { pt: "Forjando artefatos e embeddings…", en: "Forging artifacts and embeddings…" },
  "forge.idle": { pt: "Configure as quantidades e inicie a geração.", en: "Set the quantities and start generation." },
  "forge.stories": { pt: "Stories", en: "Stories" },
  "forge.bugs": { pt: "Bugs", en: "Bugs" },
  "forge.incidents": { pt: "Incidentes", en: "Incidents" },

  // Artifacts
  "artifacts.title": { pt: "Artefatos", en: "Artifacts" },
  "artifacts.subtitle": { pt: "Todos os artefatos de QA no seu grafo de conhecimento", en: "All QA artifacts in your knowledge graph" },
  "artifacts.new": { pt: "Novo Artefato", en: "New Artifact" },
  "artifacts.filterPlaceholder": { pt: "Filtrar por nome ou ID…", en: "Filter by name or ID…" },
  "artifacts.all": { pt: "Todos", en: "All" },
  "artifacts.col.type": { pt: "Tipo", en: "Type" },
  "artifacts.col.id": { pt: "ID", en: "ID" },
  "artifacts.col.name": { pt: "Nome", en: "Name" },
  "artifacts.col.date": { pt: "Data", en: "Date" },
  "artifacts.col.relationships": { pt: "Relacionamentos", en: "Relationships" },
  "artifacts.empty": { pt: "Nenhum artefato corresponde aos filtros.", en: "No artifacts match the filters." },

  // Users
  "users.title": { pt: "Usuários", en: "Users" },
  "users.subtitle": { pt: "Gerencie sua equipe de QA e níveis de acesso", en: "Manage your QA team and access levels" },
  "users.invite": { pt: "Convidar Usuário", en: "Invite User" },
  "users.col.member": { pt: "Membro", en: "Member" },
  "users.col.role": { pt: "Função", en: "Role" },
  "users.col.team": { pt: "Equipe", en: "Team" },
  "users.col.status": { pt: "Status", en: "Status" },

  // Environments
  "env.title": { pt: "Ambientes", en: "Environments" },
  "env.subtitle": { pt: "Conexões Neo4j por ambiente", en: "Neo4j connections per environment" },
  "env.current": { pt: "Atual", en: "Current" },

  // Settings
  "settings.title": { pt: "Configurações", en: "Settings" },
  "settings.subtitle": { pt: "Configure seu workspace do DefectMind", en: "Configure your DefectMind workspace" },
  "settings.neo4j": { pt: "Conexão Neo4j", en: "Neo4j Connection" },
  "settings.boltUri": { pt: "Bolt URI", en: "Bolt URI" },
  "settings.database": { pt: "Banco de Dados", en: "Database" },
  "settings.testConnection": { pt: "Testar Conexão", en: "Test Connection" },
  "settings.ai": { pt: "IA & Embeddings", en: "AI & Embeddings" },
  "settings.embedModel": { pt: "Modelo de Embedding", en: "Embedding Model" },
  "settings.autoEmbed": { pt: "Auto-embedding de novos artefatos", en: "Auto-embedding of new artifacts" },
  "settings.autoEmbed.desc": { pt: "Gerar vetores na criação", en: "Generate vectors on creation" },
  "settings.aiImpact": { pt: "Sugestões de impacto com IA", en: "AI impact suggestions" },
  "settings.aiImpact.desc": { pt: "Destacar artefatos relacionados automaticamente", en: "Highlight related artifacts automatically" },
  "settings.apiKeys": { pt: "Chaves de API", en: "API Keys" },
  "settings.prodKey": { pt: "Chave de Produção", en: "Production Key" },
  "settings.regenKey": { pt: "Regenerar Chave", en: "Regenerate Key" },
  "settings.notifications": { pt: "Notificações", en: "Notifications" },
  "settings.notif.critical": { pt: "Alertas de bugs críticos", en: "Critical bug alerts" },
  "settings.notif.incidents": { pt: "Novos incidentes", en: "New incidents" },
  "settings.notif.weekly": { pt: "Resumo semanal do grafo", en: "Weekly graph summary" },

  // Tokens (data)
  "t.Stories": { pt: "Stories", en: "Stories" },
  "t.Requisitos": { pt: "Requisitos", en: "Requirements" },
  "t.Test Cases": { pt: "Test Cases", en: "Test Cases" },
  "t.Bugs": { pt: "Bugs", en: "Bugs" },
  "t.Incidentes": { pt: "Incidentes", en: "Incidents" },
  "t.Post-mortems": { pt: "Post-mortems", en: "Post-mortems" },
  "t.thisWeek": { pt: "esta semana", en: "this week" },
  "t.Hoje": { pt: "Hoje", en: "Today" },
  "t.Ontem": { pt: "Ontem", en: "Yesterday" },
  "t.daysAgo": { pt: "dias atrás", en: "days ago" },
  "t.Alto risco": { pt: "Alto risco", en: "High risk" },
  "t.Médio risco": { pt: "Médio risco", en: "Medium risk" },
  "t.Baixo risco": { pt: "Baixo risco", en: "Low risk" },
  "t.Crítica": { pt: "Crítica", en: "Critical" },
  "t.Alta": { pt: "Alta", en: "High" },
  "t.Média": { pt: "Média", en: "Medium" },
  "t.Baixa": { pt: "Baixa", en: "Low" },
  "t.Ativo": { pt: "Ativo", en: "Active" },
  "t.Convidado": { pt: "Convidado", en: "Invited" },
  "t.Inativo": { pt: "Inativo", en: "Inactive" },
  "t.Admin": { pt: "Admin", en: "Admin" },
  "t.Líder de QA": { pt: "Líder de QA", en: "QA Lead" },
  "t.Engenheira": { pt: "Engenheira", en: "Engineer" },
  "t.Analista": { pt: "Analista", en: "Analyst" },
  "t.Visualizador": { pt: "Visualizador", en: "Viewer" },
  "t.QA Core": { pt: "QA Core", en: "QA Core" },
  "t.Pagamentos": { pt: "Pagamentos", en: "Payments" },
  "t.Plataforma": { pt: "Plataforma", en: "Platform" },
  "t.Confiabilidade": { pt: "Confiabilidade", en: "Reliability" },
  "t.Produto": { pt: "Produto", en: "Product" },
  "t.Gateway de Pagamento": { pt: "Gateway de Pagamento", en: "Payment Gateway" },
  "t.Gestão de Sessão": { pt: "Gestão de Sessão", en: "Session Management" },
  "t.Transferências": { pt: "Transferências", en: "Transfers" },
  "t.Exportação de Dados": { pt: "Exportação de Dados", en: "Data Export" },
  "t.PRODUÇÃO": { pt: "PRODUÇÃO", en: "PRODUCTION" },
  "t.Conectado": { pt: "Conectado", en: "Connected" },
};

const LangContext = createContext<{ lang: Lang; setLang: (l: Lang) => void } | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("pt");
  useEffect(() => {
    const saved = (typeof localStorage !== "undefined" && localStorage.getItem("dm-lang")) as Lang | null;
    if (saved === "pt" || saved === "en") setLangState(saved);
  }, []);
  const setLang = (l: Lang) => {
    setLangState(l);
    if (typeof localStorage !== "undefined") localStorage.setItem("dm-lang", l);
  };
  return <LangContext.Provider value={{ lang, setLang }}>{children}</LangContext.Provider>;
}

export function useLang() {
  const ctx = useContext(LangContext);
  const lang = ctx?.lang ?? "pt";
  const t = (key: string) => dict[key]?.[lang] ?? key;
  // translate a Portuguese token value (e.g. severity / status) for display
  const tt = (value: string) => dict["t." + value]?.[lang] ?? value;
  return { lang, setLang: ctx?.setLang ?? (() => {}), t, tt };
}
