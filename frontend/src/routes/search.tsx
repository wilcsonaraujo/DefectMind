import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Search, Sparkles, Clock, ArrowRight } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  searchHistory,
  searchResults,
  artifactTypeColors,
} from "@/lib/mock-data";
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
  const { t } = useLang();
  return (
    <AppLayout title={t("search.title")} subtitle={t("search.subtitle")}>
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-[minmax(0,1fr)_auto] gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={t("search.placeholder")}
                className="h-11 pl-9"
              />
            </div>
            <Button className="h-11">
              <Sparkles className="h-4 w-4" /> {t("search.button")}
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_280px]">
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            {searchResults.length} {t("search.resultsSuffix")}
          </p>
          {searchResults.map((r) => (
            <Card key={r.id} className="transition-colors hover:border-primary/40">
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={artifactTypeColors[r.type]}>
                        {r.type}
                      </Badge>
                      <span className="text-xs text-muted-foreground">{r.id}</span>
                    </div>
                    <h3 className="mt-2 truncate font-semibold">{r.title}</h3>
                    <p className="mt-1 text-sm text-muted-foreground">{r.snippet}</p>
                  </div>
                  <ArrowRight className="mt-1 h-4 w-4 shrink-0 text-muted-foreground" />
                </div>
                <div className="mt-3">
                  <ScoreBar score={r.score} />
                </div>
              </CardContent>
            </Card>
          ))}
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