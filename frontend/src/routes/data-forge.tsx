import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  FlaskConical,
  Sparkles,
  CheckCircle2,
  BookOpen,
  Bug,
  Siren,
  AlertCircle,
} from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { generateDataset, type GenerateDatasetResult } from "@/lib/api";
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
  const [numStories, setNumStories] = useState(20);
  const [batchSize, setBatchSize] = useState(5);
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerateDatasetResult | null>(null);
  const { t } = useLang();

  // Validação local antes de chamar a API
  function validate(): string | null {
    if (numStories <= 0) return "O número de stories deve ser maior que zero.";
    if (batchSize <= 0) return "O batch size deve ser maior que zero.";
    if (batchSize >= numStories) return "O batch size deve ser menor que o número de stories.";
    if (numStories % batchSize !== 0) return "O número de stories deve ser divisível pelo batch size.";
    return null;
  }

  async function generate() {
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }
    setRunning(true);
    setDone(false);
    setError(null);
    setResult(null);
    try {
      const data = await generateDataset({ num_stories: numStories, batch_size: batchSize });
      setResult(data);
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro desconhecido ao gerar dataset.");
    } finally {
      setRunning(false);
    }
  }

  const totalGenerated = result
    ? (result.stories ?? 0) +
      (result.requirements ?? 0) +
      (result.testcases ?? 0) +
      (result.bug_reports ?? 0) +
      (result.incidents ?? 0) +
      (result.postmortems ?? 0)
    : 0;

  return (
    <AppLayout title={t("forge.title")} subtitle={t("forge.subtitle")}>
      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        {/* ── Configuração ── */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FlaskConical className="h-4 w-4 text-primary" /> {t("forge.config")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="grid grid-cols-[minmax(0,1fr)_120px] items-center gap-4">
              <Label className="flex items-center gap-2 text-sm">
                <BookOpen className="h-4 w-4 text-muted-foreground" />
                {t("forge.quantityOf")} {t("forge.stories")}
              </Label>
              <Input
                type="number"
                min={1}
                value={numStories}
                onChange={(e) => setNumStories(Number(e.target.value))}
              />
            </div>
            <div className="grid grid-cols-[minmax(0,1fr)_120px] items-center gap-4">
              <Label className="flex items-center gap-2 text-sm">
                <Bug className="h-4 w-4 text-muted-foreground" />
                Batch size
                <span className="text-xs text-muted-foreground">(deve dividir stories)</span>
              </Label>
              <Input
                type="number"
                min={1}
                value={batchSize}
                onChange={(e) => setBatchSize(Number(e.target.value))}
              />
            </div>

            {error && (
              <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                {error}
              </div>
            )}

            <Button onClick={generate} disabled={running} className="w-full">
              <Sparkles className="h-4 w-4" />
              {running ? t("forge.generating") : t("forge.generate")}
            </Button>
          </CardContent>
        </Card>

        {/* ── Progresso e resultado ── */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">{t("forge.progressTitle")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">{t("forge.progress")}</span>
              <span className="font-semibold tabular-nums">
                {running ? "Em andamento…" : done ? "100%" : "0%"}
              </span>
            </div>
            <Progress value={running ? undefined : done ? 100 : 0} />

            {done && result ? (
              <>
                <div className="flex items-center gap-2 rounded-lg border border-success/30 bg-success/10 p-3 text-sm text-success">
                  <CheckCircle2 className="h-4 w-4" />
                  {totalGenerated} {t("forge.successSuffix")}
                </div>
                <div className="grid grid-cols-3 gap-2 pt-2 text-center">
                  <div className="rounded-lg bg-secondary/40 p-2">
                    <p className="text-lg font-bold">{result.stories ?? 0}</p>
                    <p className="text-[11px] text-muted-foreground">{t("forge.stories")}</p>
                  </div>
                  <div className="rounded-lg bg-secondary/40 p-2">
                    <p className="text-lg font-bold">{result.requirements ?? 0}</p>
                    <p className="text-[11px] text-muted-foreground">Requisitos</p>
                  </div>
                  <div className="rounded-lg bg-secondary/40 p-2">
                    <p className="text-lg font-bold">{result.testcases ?? 0}</p>
                    <p className="text-[11px] text-muted-foreground">Test Cases</p>
                  </div>
                  <div className="rounded-lg bg-secondary/40 p-2">
                    <p className="text-lg font-bold">{result.bug_reports ?? 0}</p>
                    <p className="text-[11px] text-muted-foreground">{t("forge.bugs")}</p>
                  </div>
                  <div className="rounded-lg bg-secondary/40 p-2">
                    <p className="text-lg font-bold">{result.incidents ?? 0}</p>
                    <p className="text-[11px] text-muted-foreground">{t("forge.incidents")}</p>
                  </div>
                  <div className="rounded-lg bg-secondary/40 p-2">
                    <p className="text-lg font-bold">{result.postmortems ?? 0}</p>
                    <p className="text-[11px] text-muted-foreground">Post-mortems</p>
                  </div>
                </div>
              </>
            ) : (
              !running && (
                <div className="grid grid-cols-3 gap-2 pt-2 text-center">
                  <div className="rounded-lg bg-secondary/40 p-2">
                    <p className="text-lg font-bold">{numStories}</p>
                    <p className="text-[11px] text-muted-foreground">{t("forge.stories")}</p>
                  </div>
                  <div className="rounded-lg bg-secondary/40 p-2">
                    <p className="text-lg font-bold">—</p>
                    <p className="text-[11px] text-muted-foreground">{t("forge.bugs")}</p>
                  </div>
                  <div className="rounded-lg bg-secondary/40 p-2">
                    <p className="text-lg font-bold">—</p>
                    <p className="text-[11px] text-muted-foreground">{t("forge.incidents")}</p>
                  </div>
                </div>
              )
            )}

            {running && (
              <p className="text-sm text-muted-foreground">{t("forge.forging")}</p>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
