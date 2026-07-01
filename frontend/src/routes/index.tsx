import { createFileRoute } from "@tanstack/react-router";
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
  CheckCircle2,
  AlertTriangle,
  GitCompareArrows,
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
  recentActivity,
  topBugs,
  severityColor,
  recentSearches,
  recentAnalyses,
  riskBadgeColor,
  artifactTypeColors,
  stories,
  type ArtifactType,
} from "@/lib/mock-data";
import { getGraphStats, type NodeByType } from "@/lib/api";
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

// ─── Ícones e cores por tipo de artefato ─────────────────────────────────────
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

const activityIcon = {
  success: { icon: CheckCircle2, cls: "text-success" },
  warning: { icon: AlertTriangle, cls: "text-warning" },
  bug: { icon: Bug, cls: "text-destructive" },
  impact: { icon: GitCompareArrows, cls: "text-primary" },
} as const;

const quickActions = [
  { key: "qa.newDataset", icon: FlaskConical, to: "/data-forge" },
  { key: "qa.exploreGraph", icon: Share2, to: "/graph" },
  { key: "qa.newSearch", icon: Search, to: "/search" },
  { key: "qa.newImpact", icon: GitCompareArrows, to: "/impact" },
] as const;

// ─── Mapeamento NodeByType → ArtifactType ────────────────────────────────────
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

// ─── Componente principal ─────────────────────────────────────────────────────
function Index() {
  const { t, tt, lang } = useLang();
  const locale = lang === "pt" ? "pt-BR" : "en-US";

  const [nodesByType, setNodesByType] = useState<NodeByType | null>(null);

  useEffect(() => {
    getGraphStats()
      .then((data) => setNodesByType(data.nodes_by_type))
      .catch(() => setNodesByType(null));
  }, []);

  const whenLabel = (w: string) => {
    if (w === "Hoje" || w === "Ontem") return tt(w);
    const m = w.match(/(\d+)\s+dias atrás/);
    if (m) return lang === "pt" ? w : `${m[1]} ${tt("daysAgo")}`;
    return w;
  };
  const timeLabel = (s: string) =>
    s.replace(/^Hoje/, tt("Hoje")).replace(/^Ontem/, tt("Ontem"));

  // Dados para o donut — usa API se disponível, senão zeros
  const donutData = NODE_TYPE_MAP.map(({ key, label }) => ({
    name: label,
    value: nodesByType?.[key] ?? 0,
    color: DONUT_COLORS[key],
  }));
  const totalNodes = donutData.reduce((a, b) => a + b.value, 0);

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

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        {/* ── Busca semântica ── */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dash.semanticSearch")}</CardTitle>
            <p className="text-sm text-muted-foreground">{t("dash.semanticSearch.desc")}</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-[minmax(0,1fr)_auto] gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input placeholder={t("dash.searchPlaceholder")} className="pl-9" />
              </div>
              <Button asChild>
                <Link to="/search">{t("dash.search")}</Link>
              </Button>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-semibold text-muted-foreground">{t("dash.recentSearches")}</p>
              {recentSearches.map((s) => (
                <div
                  key={s.query}
                  className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2 rounded-lg px-2 py-2 hover:bg-secondary/50"
                >
                  <span className="flex min-w-0 items-center gap-2 text-sm">
                    <Search className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                    <span className="truncate">{s.query}</span>
                    <Badge variant="outline" className={`${artifactTypeColors[s.tag]} shrink-0`}>
                      {s.tag}
                    </Badge>
                  </span>
                  <span className="text-xs text-muted-foreground">{whenLabel(s.when)}</span>
                </div>
              ))}
            </div>
            <Link to="/search" className="flex items-center gap-1 text-sm font-medium text-primary">
              {t("dash.viewAllSearches")} <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </CardContent>
        </Card>

        {/* ── Análise de impacto ── */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dash.impact")}</CardTitle>
            <p className="text-sm text-muted-foreground">{t("dash.impact.desc")}</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-[minmax(0,1fr)_auto] gap-2">
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder={t("dash.selectStory")} />
                </SelectTrigger>
                <SelectContent>
                  {stories.map((s) => (
                    <SelectItem key={s.id} value={s.id}>
                      {s.id} — {s.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button asChild>
                <Link to="/impact">{t("dash.analyze")}</Link>
              </Button>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-semibold text-muted-foreground">{t("dash.recentAnalyses")}</p>
              {recentAnalyses.map((a) => (
                <div
                  key={a.story}
                  className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2 rounded-lg px-2 py-2 hover:bg-secondary/50"
                >
                  <span className="flex min-w-0 items-center gap-2 text-sm">
                    <span className="truncate">{a.story}</span>
                    <Badge variant="outline" className={`${riskBadgeColor[a.risk]} shrink-0`}>
                      {tt(a.risk)}
                    </Badge>
                  </span>
                  <span className="text-xs text-muted-foreground">{whenLabel(a.when)}</span>
                </div>
              ))}
            </div>
            <Link to="/impact" className="flex items-center gap-1 text-sm font-medium text-primary">
              {t("dash.viewAllAnalyses")} <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </CardContent>
        </Card>

        {/* ── Resumo do grafo (donut) ── */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dash.graphSummary")}</CardTitle>
            <p className="text-sm text-muted-foreground">{t("dash.graphSummary.desc")}</p>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="relative h-36 w-36 shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={donutData}
                      dataKey="value"
                      innerRadius={48}
                      outerRadius={68}
                      paddingAngle={2}
                      stroke="none"
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

      {/* ── Atividade recente, top bugs e ações rápidas ── */}
      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>{t("dash.recentActivity")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {recentActivity.map((a) => {
              const meta = activityIcon[a.kind as keyof typeof activityIcon];
              const Icon = meta.icon;
              return (
                <div
                  key={a.id}
                  className="flex gap-3 rounded-lg px-2 py-2.5 hover:bg-secondary/50"
                >
                  <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${meta.cls}`} />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{a.title}</p>
                    <p className="truncate text-xs text-muted-foreground">{a.desc}</p>
                  </div>
                  <span className="shrink-0 text-xs text-muted-foreground">
                    {timeLabel(a.time)}
                  </span>
                </div>
              );
            })}
            <Link
              to="/artifacts"
              className="flex items-center gap-1 pt-2 text-sm font-medium text-primary"
            >
              {t("dash.viewAllActivity")} <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("dash.topBugs")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {topBugs.map((b, i) => (
              <div
                key={b.id}
                className="grid grid-cols-[auto_auto_minmax(0,1fr)_auto_auto] items-center gap-3 rounded-lg px-2 py-2.5 hover:bg-secondary/50"
              >
                <span className="w-3 text-sm text-muted-foreground">{i + 1}</span>
                <span className="font-mono text-xs text-muted-foreground">{b.id}</span>
                <span className="truncate text-sm">{b.title}</span>
                <Badge variant="outline" className={severityColor[b.severity]}>
                  {tt(b.severity)}
                </Badge>
                <span className="text-sm font-semibold text-muted-foreground">{b.count}</span>
              </div>
            ))}
            <Link
              to="/artifacts"
              className="flex items-center gap-1 pt-2 text-sm font-medium text-primary"
            >
              {t("dash.viewAllBugs")} <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </CardContent>
        </Card>

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
