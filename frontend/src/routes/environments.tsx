import { createFileRoute } from "@tanstack/react-router";
import { Server, CheckCircle2 } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useLang } from "@/lib/i18n";

export const Route = createFileRoute("/environments")({
  head: () => ({
    meta: [
      { title: "Ambientes — DefectMind" },
      { name: "description", content: "Gerencie ambientes e conexões do DefectMind." },
    ],
  }),
  component: EnvironmentsPage,
});

const envs = [
  { name: "DEV", uri: "bolt://dev.defectmind.dev:7687", version: "v0.1.0", status: "Conectado", current: true },
  { name: "STAGING", uri: "bolt://stg.defectmind.dev:7687", version: "v0.1.0", status: "Conectado", current: false },
  { name: "PRODUÇÃO", uri: "bolt://prod.defectmind.dev:7687", version: "v0.0.9", status: "Conectado", current: false },
];

function EnvironmentsPage() {
  const { t, tt } = useLang();
  return (
    <AppLayout title={t("env.title")} subtitle={t("env.subtitle")}>
      <div className="grid gap-4 md:grid-cols-3">
        {envs.map((e) => (
          <Card key={e.name} className={e.current ? "border-primary/50" : ""}>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div className="grid h-10 w-10 place-items-center rounded-lg bg-primary/15 text-primary">
                  <Server className="h-5 w-5" />
                </div>
                {e.current && <Badge className="bg-primary/15 text-primary">{t("env.current")}</Badge>}
              </div>
              <p className="mt-3 text-lg font-bold">{tt(e.name)}</p>
              <p className="truncate text-xs text-muted-foreground">{e.uri}</p>
              <div className="mt-3 flex items-center justify-between text-sm">
                <span className="text-muted-foreground">{e.version}</span>
                <span className="flex items-center gap-1.5 text-success">
                  <CheckCircle2 className="h-4 w-4" /> {tt(e.status)}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </AppLayout>
  );
}