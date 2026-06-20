import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  graphNodes,
  graphEdges,
  artifactTypeColors,
  type GraphNode,
  type ArtifactType,
} from "@/lib/mock-data";
import { useLang } from "@/lib/i18n";

export const Route = createFileRoute("/graph")({
  head: () => ({
    meta: [
      { title: "Explorador de Grafo — DefectMind" },
      { name: "description", content: "Visualize as relações entre artefatos de QA no grafo de conhecimento." },
    ],
  }),
  component: GraphPage,
});

const nodeFill: Record<ArtifactType, string> = {
  Story: "var(--chart-1)",
  Requirement: "var(--chart-5)",
  "Test Case": "var(--chart-2)",
  Bug: "var(--destructive)",
  Incident: "var(--warning)",
  "Post-Mortem": "var(--muted-foreground)",
};

const legend: ArtifactType[] = ["Story", "Requirement", "Test Case", "Bug", "Incident", "Post-Mortem"];

function GraphPage() {
  const [selected, setSelected] = useState<GraphNode | null>(null);
  const { t } = useLang();
  const byId = Object.fromEntries(graphNodes.map((n) => [n.id, n]));
  return (
    <AppLayout title={t("graph.title")} subtitle={t("graph.subtitle")}>
      <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
        <Card className="overflow-hidden">
          <CardContent className="p-0">
            <div className="relative aspect-[4/3] w-full bg-[radial-gradient(circle_at_center,var(--secondary)_0,transparent_70%)]">
              <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
                {graphEdges.map(([a, b], i) => {
                  const na = byId[a];
                  const nb = byId[b];
                  return (
                    <line
                      key={i}
                      x1={na.x}
                      y1={na.y}
                      x2={nb.x}
                      y2={nb.y}
                      stroke="var(--border)"
                      strokeWidth={0.4}
                    />
                  );
                })}
              </svg>
              {graphNodes.map((n) => (
                <button
                  key={n.id}
                  onClick={() => setSelected(n)}
                  className="absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center gap-1 outline-none"
                  style={{ left: `${n.x}%`, top: `${n.y}%` }}
                >
                  <span
                    className={`grid h-12 w-12 place-items-center rounded-full border-2 text-[10px] font-bold text-background transition-transform hover:scale-110 ${selected?.id === n.id ? "ring-4 ring-primary/40" : ""}`}
                    style={{ backgroundColor: nodeFill[n.type], borderColor: "var(--background)" }}
                  >
                    {n.type[0]}
                  </span>
                  <span className="whitespace-nowrap rounded bg-card px-1.5 py-0.5 text-[10px] font-medium shadow">
                    {n.label}
                  </span>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">{t("graph.legend")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {legend.map((t) => (
                <div key={t} className="flex items-center gap-2 text-sm">
                  <span className="h-3 w-3 rounded-full" style={{ backgroundColor: nodeFill[t] }} />
                  {t}
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">{t("graph.nodeDetails")}</CardTitle>
            </CardHeader>
            <CardContent>
              {selected ? (
                <div className="space-y-3">
                  <Badge variant="outline" className={artifactTypeColors[selected.type]}>
                    {selected.type}
                  </Badge>
                  <p className="font-semibold">{selected.label}</p>
                  <p className="text-sm text-muted-foreground">
                    {graphEdges.filter((e) => e.includes(selected.id)).length} {t("graph.relations")}
                  </p>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">{t("graph.clickNode")}</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}