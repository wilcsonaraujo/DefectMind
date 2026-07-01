import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  AlertCircle,
  Loader2,
  Network,
  GitBranch,
  TrendingUp,
  Layers,
  Unlink,
} from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getGraphStats, type GraphStatsResponse } from "@/lib/api";
import { useLang } from "@/lib/i18n";

export const Route = createFileRoute("/graph")({
  head: () => ({
    meta: [
      { title: "Estatísticas do Grafo — DefectMind" },
      {
        name: "description",
        content: "Métricas e estatísticas do grafo de conhecimento de artefatos de QA.",
      },
    ],
  }),
  component: GraphPage,
});

// ─── Cores por tipo de artefato ───────────────────────────────────────────────
const TYPE_COLORS: Record<string, string> = {
  Story: "#3b82f6",
  Requirement: "#8b5cf6",
  TestCase: "#10b981",
  BugReport: "#ef4444",
  Incident: "#f97316",
  PostMortem: "#f59e0b",
};

const DEFAULT_COLOR = "#6b7280";

// ─── Card de métrica ──────────────────────────────────────────────────────────
function MetricCard({
  icon: Icon,
  label,
  value,
  sub,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-5">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
          <Icon className="h-5 w-5 text-primary" />
        </div>
        <div className="min-w-0">
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="text-2xl font-bold tabular-nums">{value}</p>
          {sub && <p className="text-xs text-muted-foreground">{sub}</p>}
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Página principal ─────────────────────────────────────────────────────────
function GraphPage() {
  const [stats, setStats] = useState<GraphStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { t } = useLang();

  useEffect(() => {
    getGraphStats()
      .then(setStats)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <AppLayout title={t("graph.title")} subtitle={t("graph.subtitle")}>
        <div className="flex h-64 items-center justify-center gap-3 text-muted-foreground">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Carregando estatísticas do grafo…</span>
        </div>
      </AppLayout>
    );
  }

  if (error || !stats) {
    return (
      <AppLayout title={t("graph.title")} subtitle={t("graph.subtitle")}>
        <div className="flex h-64 flex-col items-center justify-center gap-3 text-center">
          <AlertCircle className="h-8 w-8 text-destructive" />
          <p className="text-sm text-destructive">{error ?? "Erro desconhecido."}</p>
          <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
            Tentar novamente
          </Button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout title={t("graph.title")} subtitle={t("graph.subtitle")}>

      {/* ── Cards de resumo ── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          icon={Network}
          label="Total de artefatos"
          value={stats.total_nodes.toLocaleString()}
        />
        <MetricCard
          icon={GitBranch}
          label="Total de relações"
          value={stats.total_edges.toLocaleString()}
        />
        <MetricCard
          icon={TrendingUp}
          label="Grau médio"
          value={stats.avg_degree.toFixed(2)}
          sub="relações por artefato"
        />
        <MetricCard
          icon={Layers}
          label="Densidade"
          value={(stats.density * 100).toFixed(2) + "%"}
          sub="conectividade do grafo"
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">

        {/* ── Top 10 mais conectados ── */}
        <Card>
          <CardHeader>
            <CardTitle>Top 10 artefatos mais conectados</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {stats.most_connected_nodes.length === 0 ? (
              <p className="px-6 py-4 text-sm text-muted-foreground">
                Nenhum artefato encontrado.
              </p>
            ) : (
              <div className="divide-y divide-border">
                {stats.most_connected_nodes.map((node, idx) => (
                  <div key={node.id} className="flex items-center gap-3 px-6 py-3">
                    <span className="w-5 shrink-0 text-center text-xs font-bold text-muted-foreground">
                      {idx + 1}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">
                        {node.title ?? node.id}
                      </p>
                      <Badge
                        variant="outline"
                        className="mt-0.5 text-[10px]"
                        style={{
                          borderColor: TYPE_COLORS[node.label] ?? DEFAULT_COLOR,
                          color: TYPE_COLORS[node.label] ?? DEFAULT_COLOR,
                        }}
                      >
                        {node.label}
                      </Badge>
                    </div>
                    <div className="flex shrink-0 items-center gap-1.5">
                      <span className="text-sm font-semibold tabular-nums">{node.degree}</span>
                      <span className="text-xs text-muted-foreground">rel.</span>
                      <Link to="/impact" search={{ nodeId: node.id } as never}>
                        <Button variant="ghost" size="sm" className="h-7 px-2 text-xs">
                          Ver impacto
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* ── Nós isolados ── */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Unlink className="h-4 w-4 text-muted-foreground" />
              Artefatos isolados
              {stats.isolated_nodes.length > 0 && (
                <Badge variant="destructive" className="ml-auto text-xs">
                  {stats.isolated_nodes.length}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {stats.isolated_nodes.length === 0 ? (
              <div className="flex flex-col items-center gap-2 px-6 py-8 text-center text-muted-foreground">
                <Network className="h-8 w-8 opacity-30" />
                <p className="text-sm">Todos os artefatos estão conectados.</p>
              </div>
            ) : (
              <div className="divide-y divide-border">
                {stats.isolated_nodes.map((node) => (
                  <div key={node.id} className="flex items-center gap-3 px-6 py-3">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">
                        {node.title ?? node.id}
                      </p>
                      <Badge
                        variant="outline"
                        className="mt-0.5 text-[10px]"
                        style={{
                          borderColor: TYPE_COLORS[node.label] ?? DEFAULT_COLOR,
                          color: TYPE_COLORS[node.label] ?? DEFAULT_COLOR,
                        }}
                      >
                        {node.label}
                      </Badge>
                    </div>
                    <Link to="/impact" search={{ nodeId: node.id } as never}>
                      <Button variant="ghost" size="sm" className="h-7 shrink-0 px-2 text-xs">
                        Ver impacto
                      </Button>
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

      </div>
    </AppLayout>
  );
}
