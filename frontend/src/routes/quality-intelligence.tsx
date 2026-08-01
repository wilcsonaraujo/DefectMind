import { createFileRoute } from "@tanstack/react-router";
import { useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  Flame,
  ShieldCheck,
  Puzzle,
  Rocket,
  AlertTriangle,
  Lightbulb,
  Loader2,
  AlertCircle,
  Sparkles,
  Search,
  X,
} from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import {
  getHealthScore,
  getHotspots,
  getCoverageAnalysis,
  getKnowledgeGaps,
  getReleaseReadiness,
  getRiskReport,
  getRecommendations,
  getStories,
  type HealthScoreResponse,
  type HotspotsResponse,
  type CoverageAnalysisResponse,
  type KnowledgeGapsResponse,
  type ReleaseReadinessResponse,
  type RiskReportResponse,
  type RecommendationsResponse,
  type RiskLevel,
  type VerdictType,
} from "@/lib/api";
import { useLang } from "@/lib/i18n";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/quality-intelligence")({
  head: () => ({
    meta: [
      { title: "Quality Intelligence — DefectMind" },
      {
        name: "description",
        content: "Análises de qualidade interpretadas por IA a partir do grafo de artefatos.",
      },
    ],
  }),
  component: QualityIntelligencePage,
});

// ─── Abas ──────────────────────────────────────────────────────────────────────
type TabKey =
  | "health-score"
  | "hotspots"
  | "coverage"
  | "knowledge-gaps"
  | "release-readiness"
  | "risk-report"
  | "recommendations";

const tabs: { key: TabKey; labelKey: string; icon: React.ElementType }[] = [
  { key: "health-score", labelKey: "qi.tab.healthScore", icon: Activity },
  { key: "hotspots", labelKey: "qi.tab.hotspots", icon: Flame },
  { key: "coverage", labelKey: "qi.tab.coverage", icon: ShieldCheck },
  { key: "knowledge-gaps", labelKey: "qi.tab.knowledgeGaps", icon: Puzzle },
  { key: "release-readiness", labelKey: "qi.tab.releaseReadiness", icon: Rocket },
  { key: "risk-report", labelKey: "qi.tab.riskReport", icon: AlertTriangle },
  { key: "recommendations", labelKey: "qi.tab.recommendations", icon: Lightbulb },
];

function QualityIntelligencePage() {
  const { t } = useLang();
  const [tab, setTab] = useState<TabKey>("health-score");

  return (
    <AppLayout title={t("qi.title")} subtitle={t("qi.subtitle")}>
      <div className="flex flex-wrap gap-1 overflow-x-auto border-b border-border">
        {tabs.map((item) => {
          const Icon = item.icon;
          const active = tab === item.key;
          return (
            <button
              key={item.key}
              onClick={() => setTab(item.key)}
              className={cn(
                "flex shrink-0 items-center gap-2 border-b-2 px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "border-primary text-foreground"
                  : "border-transparent text-muted-foreground hover:text-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {t(item.labelKey)}
            </button>
          );
        })}
      </div>

      <div className="mt-6">
        {tab === "health-score" && <HealthScoreTab />}
        {tab === "hotspots" && <HotspotsTab />}
        {tab === "coverage" && <CoverageTab />}
        {tab === "knowledge-gaps" && <KnowledgeGapsTab />}
        {tab === "release-readiness" && <ReleaseReadinessTab />}
        {tab === "risk-report" && <RiskReportTab />}
        {tab === "recommendations" && <RecommendationsTab />}
      </div>
    </AppLayout>
  );
}

// ─── Blocos compartilhados ─────────────────────────────────────────────────────
function RiskBadge({ level }: { level: RiskLevel }) {
  const { t } = useLang();
  const styles: Record<RiskLevel, string> = {
    LOW: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
    MEDIUM: "border-amber-500/30 bg-amber-500/10 text-amber-400",
    HIGH: "border-red-500/30 bg-red-500/10 text-red-400",
  };
  const labels: Record<RiskLevel, string> = {
    LOW: t("qi.risk.low"),
    MEDIUM: t("qi.risk.medium"),
    HIGH: t("qi.risk.high"),
  };
  return (
    <Badge variant="outline" className={styles[level]}>
      {labels[level]}
    </Badge>
  );
}

function VerdictBadge({ verdict }: { verdict: VerdictType }) {
  const { t } = useLang();
  const styles: Record<VerdictType, string> = {
    READY: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
    NEEDS_ATTENTION: "border-amber-500/30 bg-amber-500/10 text-amber-400",
    NOT_READY: "border-red-500/30 bg-red-500/10 text-red-400",
  };
  const labels: Record<VerdictType, string> = {
    READY: t("qi.verdict.ready"),
    NEEDS_ATTENTION: t("qi.verdict.needsAttention"),
    NOT_READY: t("qi.verdict.notReady"),
  };
  return (
    <Badge variant="outline" className={styles[verdict]}>
      {labels[verdict]}
    </Badge>
  );
}

function PriorityBadge({ priority }: { priority: "Low" | "Medium" | "High" }) {
  const styles: Record<string, string> = {
    Low: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
    Medium: "border-amber-500/30 bg-amber-500/10 text-amber-400",
    High: "border-red-500/30 bg-red-500/10 text-red-400",
  };
  return (
    <Badge variant="outline" className={styles[priority]}>
      {priority}
    </Badge>
  );
}

function AiAnalysisBlock({
  analysis,
  recommendations,
}: {
  analysis: string;
  recommendations: string[];
}) {
  const { t } = useLang();
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <Sparkles className="h-4 w-4" /> {t("qi.aiAnalysis")}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">{analysis}</p>
        {recommendations.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {t("qi.recommendations")}
            </p>
            <ul className="space-y-1.5">
              {recommendations.map((r, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <Lightbulb className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function ErrorCard({ message }: { message: string }) {
  return (
    <Card className="border-destructive/40">
      <CardContent className="flex items-start gap-3 p-4">
        <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />
        <p className="text-sm text-destructive">{message}</p>
      </CardContent>
    </Card>
  );
}

function ErrorCardWithRetry({ message, onRetry }: { message: string; onRetry: () => void }) {
  const { t } = useLang();
  return (
    <Card className="border-destructive/40">
      <CardContent className="flex flex-col items-start gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />
          <div>
            <p className="font-semibold text-destructive">{t("qi.loadError")}</p>
            <p className="mt-1 text-sm text-muted-foreground">{message}</p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={onRetry}>
          {t("qi.retry")}
        </Button>
      </CardContent>
    </Card>
  );
}

function LoadingBlock() {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-muted-foreground">
      <Loader2 className="h-6 w-6 animate-spin" />
    </div>
  );
}

function EmptyBlock() {
  const { t } = useLang();
  return (
    <Card>
      <CardContent className="p-8 text-center text-sm text-muted-foreground">
        {t("qi.noData")}
      </CardContent>
    </Card>
  );
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : "Erro desconhecido";
}

// ─── Tradução de valores de enum vindos do backend (SCREAMING_SNAKE_CASE) ──────
const ENUM_LABELS: Record<string, string> = {
  // GapType (Coverage Analysis)
  NO_TEST_CASE: "Sem Caso de Teste",
  NO_FUNCTIONAL_COVERAGE: "Sem Cobertura Funcional",
  ORPHAN_TEST_CASE: "Caso de Teste Órfão",
  // KnowledgeGapType
  BUG_WITHOUT_TEST_CASE: "Bug sem Caso de Teste",
  INCIDENT_WITHOUT_POSTMORTEM: "Incidente sem Postmortem",
  REQUIREMENT_WITHOUT_STORY: "Requisito sem Story",
  STORY_WITHOUT_REQUIREMENT: "Story sem Requisito",
  // RecommendationType
  EXECUTE_REGRESSION: "Executar Regressão",
  INCREASE_COVERAGE: "Aumentar Cobertura",
  CREATE_TEST_CASE: "Criar Caso de Teste",
  REVIEW_REQUIREMENT: "Revisar Requisito",
  PRIORITIZE_INTEGRATION: "Priorizar Integração",
};

// Fallback pra qualquer valor novo que o backend venha a adicionar sem o
// frontend ter sido atualizado ainda: "SOME_NEW_VALUE" → "Some New Value".
function formatEnumLabel(value: string): string {
  if (ENUM_LABELS[value]) return ENUM_LABELS[value];
  return value
    .toLowerCase()
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

// ─── Layout de 2 colunas: dados à esquerda, análise da IA fixa à direita ──────
function TwoColumnLayout({ left, right }: { left: ReactNode; right: ReactNode }) {
  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_360px] lg:items-start">
      <div className="min-w-0 space-y-4">{left}</div>
      <div className="lg:sticky lg:top-20">{right}</div>
    </div>
  );
}

// ─── Seletor de artefato (Health Score / Risk Report / Recommendations) ───────
function ArtifactSelector({
  nodeId,
  onNodeIdChange,
  onAnalyze,
  loading,
}: {
  nodeId: string;
  onNodeIdChange: (v: string) => void;
  onAnalyze: () => void;
  loading: boolean;
}) {
  const { t } = useLang();
  return (
    <Card>
      <CardContent className="grid gap-3 p-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-end">
        <div>
          <label className="mb-1.5 block text-xs font-medium text-muted-foreground">
            {t("qi.nodeIdLabel")}
          </label>
          <Input
            placeholder={t("qi.nodeIdPlaceholder")}
            value={nodeId}
            onChange={(e) => onNodeIdChange(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onAnalyze()}
          />
        </div>
        <Button className="h-10 gap-2" onClick={onAnalyze} disabled={loading || !nodeId.trim()}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          {loading ? t("qi.analyzing") : t("qi.analyze")}
        </Button>
      </CardContent>
    </Card>
  );
}

function ArtifactTabShell({
  searched,
  loading,
  error,
  children,
}: {
  searched: boolean;
  loading: boolean;
  error: string | null;
  children: ReactNode;
}) {
  const { t } = useLang();
  if (!searched && !loading) {
    return <p className="text-sm text-muted-foreground">{t("qi.selectArtifactPrompt")}</p>;
  }
  if (loading) return <LoadingBlock />;
  if (error) return <ErrorCard message={error} />;
  return <>{children}</>;
}

// ─── Aba: Health Score ─────────────────────────────────────────────────────────
function HealthScoreTab() {
  const [nodeId, setNodeId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<HealthScoreResponse | null>(null);
  const [searched, setSearched] = useState(false);

  async function handleAnalyze() {
    const id = nodeId.trim();
    if (!id) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      setData(await getHealthScore(id));
    } catch (err) {
      setError(errorMessage(err));
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <ArtifactSelector
        nodeId={nodeId}
        onNodeIdChange={setNodeId}
        onAnalyze={handleAnalyze}
        loading={loading}
      />
      <ArtifactTabShell searched={searched} loading={loading} error={error}>
        {data && (
          <TwoColumnLayout
            left={
              <>
                <Card>
                  <CardContent className="flex items-center justify-between p-4">
                    <span className="text-sm font-medium text-muted-foreground">Risk classification</span>
                    <RiskBadge level={data.risk_classification} />
                  </CardContent>
                </Card>
                {data.evidence.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Evidências</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {data.evidence.map((e, i) => (
                        <div key={i} className="rounded-lg border border-border p-3">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{e.type}</Badge>
                            <span className="text-sm font-medium">{e.artifact}</span>
                          </div>
                          <p className="mt-1 text-sm text-muted-foreground">{e.justification}</p>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}
              </>
            }
            right={
              <AiAnalysisBlock analysis={data.ai_analysis} recommendations={data.recommendations} />
            }
          />
        )}
      </ArtifactTabShell>
    </div>
  );
}

// ─── Aba: Hotspots (auto-load) ──────────────────────────────────────────────────
function HotspotsTab() {
  const { t } = useLang();
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["qi-hotspots"],
    queryFn: () => getHotspots(10),
  });

  if (isLoading) return <LoadingBlock />;
  if (error) return <ErrorCardWithRetry message={errorMessage(error)} onRetry={() => refetch()} />;
  if (!data) return null;

  return (
    <TwoColumnLayout
      left={
        <>
          {data.hotspots.length === 0 ? (
            <EmptyBlock />
          ) : (
            <div className="space-y-3">
              {data.hotspots.map((h) => (
                <Card key={h.node_id}>
                  <CardContent className="flex items-start justify-between gap-3 p-4">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{h.label}</Badge>
                        <span className="truncate text-sm font-semibold">{h.title}</span>
                      </div>
                      <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted-foreground">
                        <span>{h.bug_count} bugs</span>
                        <span>{h.critical_bug_count} críticos</span>
                        <span>{h.incident_count} incidentes</span>
                        <span>{h.postmortem_count} postmortems</span>
                      </div>
                    </div>
                    <Badge className="shrink-0">{h.score.toFixed(1)}</Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
          <p className="text-xs text-muted-foreground">
            {data.total} {t("qi.total").toLowerCase()}
          </p>
        </>
      }
      right={<AiAnalysisBlock analysis={data.ai_analysis} recommendations={data.recommendations} />}
    />
  );
}

// ─── Aba: Coverage Analysis (auto-load) ────────────────────────────────────────
function CoverageTab() {
  const { t } = useLang();
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["qi-coverage"],
    queryFn: getCoverageAnalysis,
  });

  if (isLoading) return <LoadingBlock />;
  if (error) return <ErrorCardWithRetry message={errorMessage(error)} onRetry={() => refetch()} />;
  if (!data) return null;

  return (
    <TwoColumnLayout
      left={
        <>
          <Card>
            <CardContent className="space-y-2 p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-muted-foreground">
                  {t("qi.coverageScore")}
                </span>
                <span className="text-lg font-bold tabular-nums">
                  {data.coverage_score.toFixed(1)}%
                </span>
              </div>
              <Progress value={data.coverage_score} />
            </CardContent>
          </Card>
          {data.gaps.length === 0 ? (
            <EmptyBlock />
          ) : (
            <div className="space-y-2">
              {data.gaps.map((g) => (
                <Card key={g.node_id}>
                  <CardContent className="flex items-center justify-between gap-3 p-3">
                    <div className="flex min-w-0 items-center gap-2">
                      <Badge variant="outline">{g.label}</Badge>
                      <span className="truncate text-sm">{g.title}</span>
                    </div>
                    <Badge
                      variant="outline"
                      className="shrink-0 border-amber-500/30 bg-amber-500/10 text-amber-400"
                    >
                      {formatEnumLabel(g.gap_type)}
                    </Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </>
      }
      right={<AiAnalysisBlock analysis={data.ai_analysis} recommendations={data.recommendations} />}
    />
  );
}

// ─── Aba: Knowledge Gaps (auto-load) ───────────────────────────────────────────
function KnowledgeGapsTab() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["qi-knowledge-gaps"],
    queryFn: getKnowledgeGaps,
  });

  if (isLoading) return <LoadingBlock />;
  if (error) return <ErrorCardWithRetry message={errorMessage(error)} onRetry={() => refetch()} />;
  if (!data) return null;

  return (
    <TwoColumnLayout
      left={
        data.gaps.length === 0 ? (
          <EmptyBlock />
        ) : (
          <div className="space-y-2">
            {data.gaps.map((g) => (
              <Card key={g.node_id}>
                <CardContent className="flex items-center justify-between gap-3 p-3">
                  <div className="flex min-w-0 items-center gap-2">
                    <Badge variant="outline">{g.label}</Badge>
                    <span className="truncate text-sm">{g.title}</span>
                  </div>
                  <Badge
                    variant="outline"
                    className="shrink-0 border-violet-500/30 bg-violet-500/10 text-violet-400"
                  >
                    {formatEnumLabel(g.gap_type)}
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        )
      }
      right={<AiAnalysisBlock analysis={data.ai_analysis} recommendations={data.recommendations} />}
    />
  );
}

// ─── Aba: Release Readiness (seleção múltipla de Stories) ─────────────────────
function ReleaseReadinessTab() {
  const { t } = useLang();
  const { data: stories, isLoading: storiesLoading } = useQuery({
    queryKey: ["stories"],
    queryFn: getStories,
  });

  const [storyFilter, setStoryFilter] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ReleaseReadinessResponse | null>(null);
  const [searched, setSearched] = useState(false);

  const filteredStories = (stories ?? []).filter((s) =>
    s.title.toLowerCase().includes(storyFilter.trim().toLowerCase()),
  );
  const selectedStories = (stories ?? []).filter((s) => selected.includes(s.id));

  function toggleStory(id: string) {
    setSelected((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]));
  }

  function removeStory(id: string) {
    setSelected((prev) => prev.filter((s) => s !== id));
  }

  async function handleAnalyze() {
    if (selected.length === 0) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      setData(await getReleaseReadiness(selected));
    } catch (err) {
      setError(errorMessage(err));
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">{t("qi.selectStories")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              className="pl-9"
              placeholder={t("qi.searchStoriesPlaceholder")}
              value={storyFilter}
              onChange={(e) => setStoryFilter(e.target.value)}
            />
          </div>

          {storiesLoading ? (
            <LoadingBlock />
          ) : (
            <div className="max-h-64 space-y-1 overflow-y-auto rounded-lg border border-border p-2">
              {filteredStories.length === 0 ? (
                <p className="px-2 py-3 text-center text-xs text-muted-foreground">
                  {t("qi.noData")}
                </p>
              ) : (
                filteredStories.map((s) => (
                  <label
                    key={s.id}
                    className="flex cursor-pointer items-center gap-2.5 rounded-md px-2 py-1.5 text-sm hover:bg-secondary"
                  >
                    <Checkbox
                      checked={selected.includes(s.id)}
                      onCheckedChange={() => toggleStory(s.id)}
                    />
                    <span className="truncate">{s.title}</span>
                  </label>
                ))
              )}
            </div>
          )}

          {selectedStories.length > 0 && (
            <div>
              <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                {selectedStories.length} {t("qi.storiesSelectedSuffix")}
              </p>
              <div className="flex flex-wrap gap-1.5">
                {selectedStories.map((s) => (
                  <Badge key={s.id} variant="secondary" className="gap-1.5 py-1 pl-2.5 pr-1.5">
                    <span className="max-w-[200px] truncate">{s.title}</span>
                    <button
                      onClick={() => removeStory(s.id)}
                      className="rounded-full p-0.5 hover:bg-background/60"
                      aria-label={`Remover ${s.title}`}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end">
            <Button className="gap-2" onClick={handleAnalyze} disabled={loading || selected.length === 0}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Rocket className="h-4 w-4" />}
              {loading ? t("qi.analyzing") : t("qi.analyze")}
            </Button>
          </div>
        </CardContent>
      </Card>

      {!searched && !loading && (
        <p className="text-sm text-muted-foreground">{t("qi.noStoriesSelected")}</p>
      )}
      {loading && <LoadingBlock />}
      {!loading && error && <ErrorCard message={error} />}
      {!loading && !error && data && (
        <TwoColumnLayout
          left={data.results.map((r) => (
            <Card key={r.story_id}>
              <CardContent className="space-y-3 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-sm font-semibold">{r.title}</span>
                  <VerdictBadge verdict={r.verdict} />
                </div>
                <div className="grid grid-cols-3 gap-3 text-xs">
                  <div>
                    <p className="text-muted-foreground">{t("qi.coverageScore")}</p>
                    <p className="font-semibold tabular-nums">{r.coverage_score.toFixed(1)}%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">{t("qi.healthRisk")}</p>
                    <RiskBadge level={r.health_risk} />
                  </div>
                  <div>
                    <p className="text-muted-foreground">{t("qi.incidentsWithoutPostmortem")}</p>
                    <p className="font-semibold tabular-nums">{r.incidents_count}</p>
                  </div>
                </div>
                {r.blockers.length > 0 && (
                  <div>
                    <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                      {t("qi.blockers")}
                    </p>
                    <ul className="space-y-1">
                      {r.blockers.map((b, i) => (
                        <li key={i} className="text-sm text-muted-foreground">
                          • {b}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
          right={<AiAnalysisBlock analysis={data.ai_analysis} recommendations={data.recommendations} />}
        />
      )}
    </div>
  );
}

// ─── Aba: Risk Report ───────────────────────────────────────────────────────────
function RiskReportTab() {
  const [nodeId, setNodeId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RiskReportResponse | null>(null);
  const [searched, setSearched] = useState(false);

  async function handleAnalyze() {
    const id = nodeId.trim();
    if (!id) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      setData(await getRiskReport(id));
    } catch (err) {
      setError(errorMessage(err));
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <ArtifactSelector
        nodeId={nodeId}
        onNodeIdChange={setNodeId}
        onAnalyze={handleAnalyze}
        loading={loading}
      />
      <ArtifactTabShell searched={searched} loading={loading} error={error}>
        {data && (
          <TwoColumnLayout
            left={
              data.risks.length > 0 ? (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Riscos identificados</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {data.risks.map((risk, i) => (
                      <div key={i} className="rounded-lg border border-border p-3">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{risk.type}</Badge>
                          <span className="text-sm font-medium">{risk.artifact}</span>
                        </div>
                        <p className="mt-1 text-sm text-muted-foreground">{risk.justification}</p>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              ) : (
                <EmptyBlock />
              )
            }
            right={
              <AiAnalysisBlock analysis={data.ai_analysis} recommendations={data.recommendations} />
            }
          />
        )}
      </ArtifactTabShell>
    </div>
  );
}

// ─── Aba: Recommendations ───────────────────────────────────────────────────────
function RecommendationsTab() {
  const { t } = useLang();
  const [nodeId, setNodeId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RecommendationsResponse | null>(null);
  const [searched, setSearched] = useState(false);

  async function handleAnalyze() {
    const id = nodeId.trim();
    if (!id) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      setData(await getRecommendations(id));
    } catch (err) {
      setError(errorMessage(err));
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <ArtifactSelector
        nodeId={nodeId}
        onNodeIdChange={setNodeId}
        onAnalyze={handleAnalyze}
        loading={loading}
      />
      <ArtifactTabShell searched={searched} loading={loading} error={error}>
        {data && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Sparkles className="h-4 w-4" /> {t("qi.aiAnalysis")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{data.ai_analysis}</p>
              </CardContent>
            </Card>
            {data.recommendations.length === 0 ? (
              <EmptyBlock />
            ) : (
              <div className="space-y-3">
                {data.recommendations.map((r, i) => (
                  <Card key={i}>
                    <CardContent className="p-4">
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge variant="outline">{formatEnumLabel(r.type)}</Badge>
                        <PriorityBadge priority={r.priority} />
                      </div>
                      <p className="mt-2 text-sm text-muted-foreground">{r.justification}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </ArtifactTabShell>
    </div>
  );
}
