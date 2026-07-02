import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  Plus,
  Search,
  FlaskConical,
  Share2,
  FileText,
  BookOpen,
  ClipboardCheck,
  Bug,
  Siren,
  ScrollText,
  ArrowRight,
  Network,
  Loader2,
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  getGraphStats,
  getStories,
  getBugReports,
  getIncidents,
  type NodeByType,
  type StoryResponse,
  type BugReportResponse,
  type IncidentResponse,
} from "@/lib/api";
import { useLang } from "@/lib/i18n";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Dashboard — DefectMind" },
      { name: "description", content: "Overview of QA artifacts, bugs and graph activity in DefectMind." },
    ],
  }),
  component: Index,
});

// ─── Tipos e constantes ───────────────────────────────────────────────────────
type ArtifactType = "Story" | "Requirement" | "Test Case" | "Bug" | "Incident" | "Post-Mortem";

const statIcons: Record<ArtifactType, typeof FileText> = {
  Story: BookOpen,
  Requirement: FileText,
  "Test Case": ClipboardCheck,
  Bug: Bug,
  Incident: Siren,
  "Post-Mortem": ScrollText,
};
const statTint: Record<ArtifactType, string> = {
  Story: "bg-chart-1/15 text-chart-1",
  Requirement: "bg-chart-2/15 text-chart-2",
  "Test Case": "bg-chart-3/15 text-chart-3",
  Bug: "bg-destructive/15 text-destructive",
  Incident: "bg-warning/15 text-warning",
  "Post-Mortem": "bg-primary/15 text-primary",
};
const quickActions = [
  { key: "qa.newDataset", icon: FlaskConical, to: "/data-forge" },
  { key: "qa.exploreGraph", icon: Share2, to: "/graph" },
  { key: "qa.newSearch", icon: Search, to: "/search" },
  { key: "qa.newImpact", icon: Network, to: "/impact" },
] as const;

const NODE_TYPE_MAP: { key: keyof NodeByType; type: ArtifactType; label: string }[] = [
  { key: "Story",       type: "Story",       label: "Stories"      },
  { key: "Requirement", type: "Requirement", label: "Requisitos"   },
  { key: "TestCase",    type: "Test Case",   label: "Test Cases"   },
  { key: "BugReport",   type: "Bug",         label: "Bugs"         },
  { key: "Incident",    type: "Incident",    label: "Incidentes"   },
  { key: "PostMortem",  type: "Post-Mortem", label: "Post-mortems" },
];
const DONUT_COLORS: Record<keyof NodeByType, string> = {
  Story:       "var(--chart-1)",
  Requirement: "var(--chart-2)",
  TestCase:    "var(--chart-3)",
  BugReport:   "var(--chart-4)",
  Incident:    "var(--chart-5)",
  PostMortem:  "oklch(0.7 0.17 330)",
};
const severityColor: Record<string, string> = {
  Critical: "bg-destructive/15 text-destructive border-destructive/30",
  High:     "bg-warning/15 text-warning border-warning/30",
  Medium:   "bg-chart-5/15 text-chart-5 border-chart-5/30",
  Low:      "bg-success/15 text-success border-success/30",
};
const severityOrder: Record<string, number> = {
  Critical: 0, High: 1, Medium: 2, Low: 3,
};

// ─── Componente principal ─────────────────────────────────────────────────────
function Index() {
  const { t, lang } = useLang();
  const navigate = useNavigate();
  const locale = lang === "pt" ? "pt-BR" : "en-US";

  // Estado dos dados
  const [nodesByType, setNodesByType] = useState<NodeByType | null>(null);
  const [stories, setStories] = useState<StoryResponse[]>([]);
  const [topBugs, setTopBugs] = useState<BugReportResponse[]>([]);
  const [recentActivity, setRecentActivity] = useState<IncidentResponse[]>([]);
  const [selectedStory, setSelectedStory] = useState<string>("");

  // Estado da busca semântica inline
  const [searchQuery, setSearchQuery] = useState("");
  const [searchLoading, setSearchLoading] = useState(false);

  useEffect(() => {
    // Estatísticas do grafo e donut
    getGraphStats()
      .then((data) => setNodesByType(data.nodes_by_type))
      .catch(() => setNodesByType(null));

    // Stories para o select de análise de impacto
    getStories()
      .then(setStories)
      .catch(() => setStories([]));

    // Top bugs por severidade
    getBugReports()
      .then((bugs) => {
        const sorted = [...bugs].sort(
          (a, b) => (severityOrder[a.severity] ?? 99) - (severityOrder[b.severity] ?? 99),
        );
        setTopBugs(sorted.slice(0, 5));
      })
      .catch(() => setTopBugs([]));

    // Atividade recente: últimos incidentes criados
    getIncidents()
      .then((incidents) => {
        const sorted = [...incidents].sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
        );
        setRecentActivity(sorted.slice(0, 5));
      })
      .catch(() => setRecentActivity([]));
  }, []);

  // Busca semântica inline: navega para /search com a query
  function handleSearch() {
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    navigate({ to: "/search", search: { q: searchQuery } }).finally(() =>
      setSearchLoading(false),
    );
  }

  // Donut data
  const donutData = NODE_TYPE_MAP.map(({ key, label }) => ({
    name: label,
    value: nodesByType?.[key] ?? 0,
    color: DONUT_COLORS[key],
  }));
  const totalNodes = donutData.reduce((a, b) => a + b.value, 0);

  // Formatar data relativa
  function relativeDate(iso: string): string {
    const diff = Date.now() - new Date(iso).getTime();
    const days = Math.floor(diff / 86_400_000);
    if (days === 0) return lang === "pt" ? "Hoje" : "Today";
    if (days === 1) return lang === "pt" ? "Ontem" : "Yesterday";
    return lang === "pt" ? `${days} dias atrás` : `${days} days ago`;
  }

  return (
    <AppLayout
      title={t("dash.title")}
      subtitle={t("dash.subtitle")}
      actions={
        <Button asChild>
          <Link to="/data-forge">
            <Plus className="h-4 w-4" /> {t("dash.generateDataset")}
          </Link>
        </Button>
      }
    >
      {/* ── Cards de totais por tipo ── */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
        {NODE_TYPE_MAP.map(({ key, type, label }) => {
          const Icon = statIcons[type];
          const value = nodesByType?.[key] ?? 0;
          return (
            <Card key={key}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <p className="text-sm font-medium text-muted-foreground">{label}</p>
                  <div className={`grid h-9 w-9 place-items-center rounded-lg ${statTint[type]}`}>
                    <Icon className="h-4 w-4" />
                  </div>
                </div>
                <p className="mt-2 text-2xl font-bold tracking-tight">
                  {nodesByType === null ? "—" : value.toLocaleString(locale)}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* ── Linha 2: Busca, Impacto, Grafo ── */}
      <div className="mt-6 grid gap-6 xl:grid-cols-3">

        {/* ── Busca Semântica ── */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dash.semanticSearch")}</CardTitle>
            <p className="text-sm text-muted-foreground">{t("dash.semanticSearch.desc")}</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-[minmax(0,1fr)_auto] gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder={t("dash.searchPlaceholder")}
                  className="pl-9"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                />
              </div>
              <Button onClick={handleSearch} disabled={searchLoading || !searchQuery.trim()}>
                {searchLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  t("dash.search")
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              {lang === "pt"
                ? "Digite uma consulta em linguagem natural para buscar artefatos por similaridade semântica."
                : "Type a natural language query to search artifacts by semantic similarity."}
            </p>
            <Link to="/search" className="flex items-center gap-1 text-sm font-medium text-primary">
              {t("dash.viewAllSearches")} <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </CardContent>
        </Card>

        {/* ── Análise de Impacto ── */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dash.impact")}</CardTitle>
            <p className="text-sm text-muted-foreground">{t("dash.impact.desc")}</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-[minmax(0,1fr)_auto] gap-2">
              <Select value={selectedStory} onValueChange={setSelectedStory}>
                <SelectTrigger>
                  <SelectValue
                    placeholder={
                      stories.length === 0
                        ? lang === "pt" ? "Carregando stories…" : "Loading stories…"
                        : t("dash.selectStory")
                    }
                  />
                </SelectTrigger>
                <SelectContent>
                  {stories.length === 0 ? (
                    <SelectItem value="none" disabled>
                      {lang === "pt" ? "Nenhuma story disponível" : "No stories available"}
                    </SelectItem>
                  ) : (
                    stories.map((s) => (
                      <SelectItem key={s.id} value={s.id}>
                        {s.title}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
              <Button asChild disabled={!selectedStory}>
                <Link to="/impact" search={selectedStory ? { nodeId: selectedStory } : {}}>
                  {t("dash.analyze")}
                </Link>
              </Button>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-semibold text-muted-foreground">
                {lang === "pt" ? `${stories.length} stories disponíveis` : `${stories.length} stories available`}
              </p>
              {stories.slice(0, 3).map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 hover:bg-secondary/50"
                >
                  <span className="truncate text-sm">{s.title}</span>
                  <Button variant="ghost" size="sm" className="h-6 shrink-0 px-2 text-xs" asChild>
                    <Link to="/impact" search={{ nodeId: s.id }}>
                      <Network className="mr-1 h-3 w-3" />
                      {lang === "pt" ? "Ver" : "View"}
                    </Link>
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* ── Grafo de conhecimento ── */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dash.knowledgeGraph")}</CardTitle>
            <p className="text-sm text-muted-foreground">{t("dash.knowledgeGraph.desc")}</p>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="relative h-36 w-36 shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={donutData}
                      cx="50%"
                      cy="50%"
                      innerRadius={44}
                      outerRadius={64}
                      dataKey="value"
                      strokeWidth={0}
                    >
                      {donutData.map((d) => (
                        <Cell key={d.name} fill={d.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-lg font-bold">{totalNodes.toLocaleString(locale)}</span>
                  <span className="text-[11px] text-muted-foreground">{t("dash.total")}</span>
                </div>
              </div>
              <div className="min-w-0 flex-1 space-y-1.5">
                {donutData.map((d) => (
                  <div key={d.name} className="flex items-center gap-2 text-sm">
                    <span
                      className="h-2.5 w-2.5 shrink-0 rounded-full"
                      style={{ backgroundColor: d.color }}
                    />
                    <span className="truncate">{d.name}</span>
                    <span className="ml-auto text-muted-foreground">
                      {d.value.toLocaleString(locale)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            <Link
              to="/graph"
              className="mt-4 flex items-center gap-1 text-sm font-medium text-primary"
            >
              {t("dash.exploreFullGraph")} <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* ── Linha 3: Atividade recente, Top Bugs, Ações rápidas ── */}
      <div className="mt-6 grid gap-6 xl:grid-cols-3">

        {/* ── Atividade recente (últimos incidentes) ── */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dash.recentActivity")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {recentActivity.length === 0 ? (
              <p className="px-2 py-4 text-sm text-muted-foreground">
                {lang === "pt" ? "Nenhum incidente registrado." : "No incidents recorded."}
              </p>
            ) : (
              recentActivity.map((inc) => (
                <div
                  key={inc.id}
                  className="flex gap-3 rounded-lg px-2 py-2.5 hover:bg-secondary/50"
                >
                  <Siren className="mt-0.5 h-4 w-4 shrink-0 text-warning" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{inc.title}</p>
                    <p className="truncate text-xs text-muted-foreground">{inc.description}</p>
                  </div>
                  <span className="shrink-0 text-xs text-muted-foreground">
                    {relativeDate(inc.created_at)}
                  </span>
                </div>
              ))
            )}
            <Link
              to="/artifacts"
              className="flex items-center gap-1 pt-2 text-sm font-medium text-primary"
            >
              {t("dash.viewAllActivity")} <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </CardContent>
        </Card>

        {/* ── Top Bugs por Severidade ── */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dash.topBugs")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {topBugs.length === 0 ? (
              <p className="px-2 py-4 text-sm text-muted-foreground">
                {lang === "pt" ? "Nenhum bug registrado." : "No bugs recorded."}
              </p>
            ) : (
              topBugs.map((b, i) => (
                <div
                  key={b.id}
                  className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 rounded-lg px-2 py-2.5 hover:bg-secondary/50"
                >
                  <span className="w-4 text-sm text-muted-foreground">{i + 1}</span>
                  <span className="truncate text-sm">{b.title}</span>
                  <Badge variant="outline" className={severityColor[b.severity] ?? ""}>
                    {b.severity}
                  </Badge>
                </div>
              ))
            )}
            <Link
              to="/artifacts"
              className="flex items-center gap-1 pt-2 text-sm font-medium text-primary"
            >
              {t("dash.viewAllBugs")} <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </CardContent>
        </Card>

        {/* ── Ações rápidas ── */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dash.quickActions")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {quickActions.map((q) => (
              <Link
                key={q.key}
                to={q.to}
                className="flex items-center gap-3 rounded-xl border border-border bg-secondary/40 p-3 transition-colors hover:border-primary/40 hover:bg-secondary"
              >
                <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-primary/15 text-primary">
                  <q.icon className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{t(q.key)}</p>
                  <p className="truncate text-xs text-muted-foreground">{t(q.key + ".desc")}</p>
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
