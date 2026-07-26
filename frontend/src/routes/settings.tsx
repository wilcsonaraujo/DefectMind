import { createFileRoute } from "@tanstack/react-router";
import { Database, Cpu, KeyRound, Bell, Info } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { useLang } from "@/lib/i18n";

// Esta página ainda não está ligada a nenhuma API — os valores abaixo são
// só exemplo. Tudo fica desabilitado pra não parecer que dá pra editar
// e salvar algo que na verdade não vai a lugar nenhum.
const PREVIEW_ONLY = true;

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Configurações — DefectMind" },
      { name: "description", content: "Configure conexões, IA e notificações do DefectMind." },
    ],
  }),
  component: SettingsPage,
});

function SettingsPage() {
  const { t } = useLang();
  return (
    <AppLayout title={t("settings.title")} subtitle={t("settings.subtitle")}>
      <div className="mb-4 flex items-start gap-2 rounded-lg border border-border bg-secondary/40 px-4 py-3 text-sm text-muted-foreground">
        <Info className="mt-0.5 h-4 w-4 shrink-0" />
        <p>Pré-visualização — esta tela ainda não está conectada a nenhuma API. Os campos abaixo são somente para exemplo.</p>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Database className="h-4 w-4 text-primary" /> {t("settings.neo4j")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <Label>{t("settings.boltUri")}</Label>
              <Input defaultValue="bolt://graph.defectmind.io:7687" disabled={PREVIEW_ONLY} />
            </div>
            <div className="space-y-1.5">
              <Label>{t("settings.database")}</Label>
              <Input defaultValue="defectmind" disabled={PREVIEW_ONLY} />
            </div>
            <Button variant="outline" disabled={PREVIEW_ONLY} title="Ainda não implementado">
              {t("settings.testConnection")}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Cpu className="h-4 w-4 text-primary" /> {t("settings.ai")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <Label>{t("settings.embedModel")}</Label>
              <Input defaultValue="text-embedding-3-large" disabled={PREVIEW_ONLY} />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{t("settings.autoEmbed")}</p>
                <p className="text-xs text-muted-foreground">{t("settings.autoEmbed.desc")}</p>
              </div>
              <Switch defaultChecked disabled={PREVIEW_ONLY} />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{t("settings.aiImpact")}</p>
                <p className="text-xs text-muted-foreground">{t("settings.aiImpact.desc")}</p>
              </div>
              <Switch defaultChecked disabled={PREVIEW_ONLY} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <KeyRound className="h-4 w-4 text-primary" /> {t("settings.apiKeys")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <Label>{t("settings.prodKey")}</Label>
              <Input type="password" defaultValue="dm_live_••••••••••••" disabled={PREVIEW_ONLY} />
            </div>
            <Button variant="outline" disabled={PREVIEW_ONLY} title="Ainda não implementado">
              {t("settings.regenKey")}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Bell className="h-4 w-4 text-primary" /> {t("settings.notifications")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {["settings.notif.critical", "settings.notif.incidents", "settings.notif.weekly"].map((n, i) => (
              <div key={n} className="flex items-center justify-between">
                <p className="text-sm font-medium">{t(n)}</p>
                <Switch defaultChecked={i !== 2} disabled={PREVIEW_ONLY} />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}