import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { FlaskConical, Sparkles, CheckCircle2, BookOpen, Bug, Siren } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useLang } from "@/lib/i18n";

export const Route = createFileRoute("/data-forge")({
  head: () => ({
    meta: [
      { title: "Data Forge — DefectMind" },
      { name: "description", content: "Gere datasets sintéticos de QA para testes e demonstrações." },
    ],
  }),
  component: DataForgePage,
});

function DataForgePage() {
  const [stories, setStories] = useState(50);
  const [bugs, setBugs] = useState(120);
  const [incidents, setIncidents] = useState(10);
  const [progress, setProgress] = useState(0);
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);
  const { t } = useLang();

  function generate() {
    setRunning(true);
    setDone(false);
    setProgress(0);
    const timer = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(timer);
          setRunning(false);
          setDone(true);
          return 100;
        }
        return p + 5;
      });
    }, 120);
  }

  const fields = [
    { label: t("forge.stories"), value: stories, set: setStories, icon: BookOpen },
    { label: t("forge.bugs"), value: bugs, set: setBugs, icon: Bug },
    { label: t("forge.incidents"), value: incidents, set: setIncidents, icon: Siren },
  ];

  return (
    <AppLayout title={t("forge.title")} subtitle={t("forge.subtitle")}>
      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FlaskConical className="h-4 w-4 text-primary" /> {t("forge.config")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            {fields.map((f) => (
              <div key={f.label} className="grid grid-cols-[minmax(0,1fr)_120px] items-center gap-4">
                <Label className="flex items-center gap-2 text-sm">
                  <f.icon className="h-4 w-4 text-muted-foreground" /> {t("forge.quantityOf")} {f.label}
                </Label>
                <Input
                  type="number"
                  min={0}
                  value={f.value}
                  onChange={(e) => f.set(Number(e.target.value))}
                />
              </div>
            ))}
            <Button onClick={generate} disabled={running} className="w-full">
              <Sparkles className="h-4 w-4" />
              {running ? t("forge.generating") : t("forge.generate")}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">{t("forge.progressTitle")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">{t("forge.progress")}</span>
              <span className="font-semibold tabular-nums">{progress}%</span>
            </div>
            <Progress value={progress} />
            {done ? (
              <div className="flex items-center gap-2 rounded-lg border border-success/30 bg-success/10 p-3 text-sm text-success">
                <CheckCircle2 className="h-4 w-4" />
                {stories + bugs + incidents} {t("forge.successSuffix")}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                {running ? t("forge.forging") : t("forge.idle")}
              </p>
            )}
            <div className="grid grid-cols-3 gap-2 pt-2 text-center">
              <div className="rounded-lg bg-secondary/40 p-2">
                <p className="text-lg font-bold">{stories}</p>
                <p className="text-[11px] text-muted-foreground">{t("forge.stories")}</p>
              </div>
              <div className="rounded-lg bg-secondary/40 p-2">
                <p className="text-lg font-bold">{bugs}</p>
                <p className="text-[11px] text-muted-foreground">{t("forge.bugs")}</p>
              </div>
              <div className="rounded-lg bg-secondary/40 p-2">
                <p className="text-lg font-bold">{incidents}</p>
                <p className="text-[11px] text-muted-foreground">{t("forge.incidents")}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}