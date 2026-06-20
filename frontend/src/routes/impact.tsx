import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Bug, Siren, AlertTriangle } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  stories,
  relatedBugs,
  relatedIncidents,
  riskAreas,
  severityColor,
} from "@/lib/mock-data";
import { useLang } from "@/lib/i18n";

export const Route = createFileRoute("/impact")({
  head: () => ({
    meta: [
      { title: "Análise de Impacto — DefectMind" },
      { name: "description", content: "Analise o raio de impacto de uma story em bugs e incidentes." },
    ],
  }),
  component: ImpactPage,
});

function ImpactPage() {
  const [story, setStory] = useState(stories[0].id);
  const { t, tt } = useLang();
  return (
    <AppLayout title={t("impact.title")} subtitle={t("impact.subtitle")}>
      <Card>
        <CardContent className="grid gap-4 p-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted-foreground">
              {t("impact.selectStory")}
            </label>
            <Select value={story} onValueChange={setStory}>
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {stories.map((s) => (
                  <SelectItem key={s.id} value={s.id}>
                    {s.id} — {s.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex gap-4 sm:gap-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-destructive">{relatedBugs.length}</p>
              <p className="text-xs text-muted-foreground">{t("impact.bugs")}</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-warning">{relatedIncidents.length}</p>
              <p className="text-xs text-muted-foreground">{t("impact.incidents")}</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary">{riskAreas.length}</p>
              <p className="text-xs text-muted-foreground">{t("impact.riskAreas")}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Bug className="h-4 w-4 text-destructive" /> {t("impact.relatedBugs")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {relatedBugs.map((b) => (
              <div key={b.id} className="rounded-lg border border-border p-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">{b.id}</span>
                  <Badge variant="outline" className={severityColor[b.severity]}>
                    {tt(b.severity)}
                  </Badge>
                </div>
                <p className="mt-1.5 text-sm font-medium">{b.title}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Siren className="h-4 w-4 text-warning" /> {t("impact.relatedIncidents")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {relatedIncidents.map((i) => (
              <div key={i.id} className="rounded-lg border border-border p-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">{i.id}</span>
                  <Badge variant="outline" className={severityColor[i.impact] ?? ""}>
                    {t("impact.impactPrefix")} {tt(i.impact)}
                  </Badge>
                </div>
                <p className="mt-1.5 text-sm font-medium">{i.title}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <AlertTriangle className="h-4 w-4 text-primary" /> {t("impact.riskAreas")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 pt-2">
            {riskAreas.map((r) => (
              <div key={r.area}>
                <div className="mb-1.5 flex items-center justify-between text-sm">
                  <span className="font-medium">{tt(r.area)}</span>
                  <span className="text-muted-foreground">{r.level}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-secondary">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-primary to-destructive"
                    style={{ width: `${r.level}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}