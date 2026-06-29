import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Search, Sparkles, Clock, ArrowRight, AlertCircle, Loader2 } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { searchHistory } from "@/lib/mock-data";
import { searchSemantic, type SearchResult, type EntityType } from "@/lib/api";
import { useLang } from "@/lib/i18n";

export const Route = createFileRoute("/search")({
  head: () => ({
    meta: [
      { title: "Busca Semântica — DefectMind" },
      { name: "description", content: "Busca semântica em artefatos de QA usando embeddings." },
    ],
  }),
  component: SearchPage,
});

const entityTypes: EntityType[] = [
  "Story",
  "Requirement",
  "TestCase",
  "BugReport",
  "Incident",
  "PostMortem",
];

const entityTypeColors: Record<EntityType, string> = {
  Story: "border-blue-500/30 bg-blue-500/10 text-blue-400",
  Requirement: "border-violet-500/30 bg-violet-500/10 text-violet-400",
  TestCase: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
  BugReport: "border-red-500/30 bg-red-500/10 text-red-400",
  Incident: "border-orange-500/30 bg-orange-500/10 text-orange-400",
  PostMortem: "border-amber-500/30 bg-amber-500/10 text-amber-400",
};

function ScoreBar({ score }: { score: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 overflow-hidden rounded-full bg-secondary">
        <div className="h-full rounded-full bg-primary" style={{ width: `${score * 100}%` }} />
      </div>
      <span className="text-xs font-semibold tabular-nums text-primary">{score.toFixed(2)}</span>
    </div>
  );
}

function SearchPage() {
  const [query, setQuery] = useState("falhas de autenticação por timeout");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<EntityType | null>(null);
  const [searched, setSearched] = useState(false);
  const { t } = useLang();

  async function handleSearch() {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      const data = await searchSemantic({ text: query, filter, limit_responses: 10 });
      setResults(data.results);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro desconhecido");
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout title={t("search.title")} subtitle={t("search.subtitle")}>
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-[minmax(0,1fr)_auto_auto]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                placeholder={t("search.placeholder")}
                className="h-11 pl-9"
              />
            </div>
            <Select
              value={filter ?? "all"}
              onValueChange={(v) => setFilter(v === "all" ? null : (v as EntityType))}
            >
              <SelectTrigger className="h-11 sm:w-44">
                <SelectValue placeholder={t("search.filterPlaceholder")} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t("artifacts.all")}</SelectItem>
                {entityTypes.map((et) => (
                  <SelectItem key={et} value={et}>
                    {et}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button className="h-11" onClick={handleSearch} disabled={loading}>
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}{" "}
              {loading ? t("search.loading") : t("search.button")}
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_280px]">
        <div className="space-y-3">
          {searched && !loading && !error && (
            <p className="text-sm text-muted-foreground">
              {total} {t("search.resultsSuffix")}
            </p>
          )}

          {loading && (
            <div className="space-y-3">
              {[0, 1, 2].map((i) => (
                <Card key={i}>
                  <CardContent className="space-y-3 p-4">
                    <div className="h-4 w-1/3 animate-pulse rounded bg-secondary" />
                    <div className="h-4 w-2/3 animate-pulse rounded bg-secondary" />
                    <div className="h-3 w-1/4 animate-pulse rounded bg-secondary" />
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {!loading && error && (
            <Card className="border-destructive/40">
              <CardContent className="flex items-start gap-3 p-4">
                <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />
                <div className="min-w-0">
                  <p className="font-semibold text-destructive">{t("search.error")}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{error}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {!loading && !error && searched && results.length === 0 && (
            <Card>
              <CardContent className="flex flex-col items-center gap-2 p-10 text-center">
                <Search className="h-6 w-6 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">{t("search.noResults")}</p>
              </CardContent>
            </Card>
          )}

          {!loading &&
            !error &&
            results.map((r) => {
              const props = r.properties as Record<string, unknown>;
              const title =
                (props.title as string) ?? (props.description as string) ?? r.id;
              const snippet = (props.description as string) ?? "";
              return (
                <Card key={r.id} className="transition-colors hover:border-primary/40">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className={entityTypeColors[r.label]}>
                            {r.label}
                          </Badge>
                          <span className="text-xs text-muted-foreground">{r.id}</span>
                        </div>
                        <h3 className="mt-2 truncate font-semibold">{title}</h3>
                        {snippet && (
                          <p className="mt-1 text-sm text-muted-foreground">{snippet}</p>
                        )}
                      </div>
                      <ArrowRight className="mt-1 h-4 w-4 shrink-0 text-muted-foreground" />
                    </div>
                    <div className="mt-3">
                      <ScoreBar score={r.score} />
                    </div>
                  </CardContent>
                </Card>
              );
            })}
        </div>

        <Card className="h-fit">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Clock className="h-4 w-4" /> {t("search.history")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {searchHistory.map((h) => (
              <button
                key={h}
                onClick={() => setQuery(h)}
                className="flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              >
                <Search className="h-3.5 w-3.5 shrink-0" />
                <span className="truncate">{h}</span>
              </button>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}