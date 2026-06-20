import { createFileRoute } from "@tanstack/react-router";
import { Database, Cpu, KeyRound, Bell } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { useLang } from "@/lib/i18n";

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
              <Input defaultValue="bolt://graph.defectmind.io:7687" />
            </div>
            <div className="space-y-1.5">
              <Label>{t("settings.database")}</Label>
              <Input defaultValue="defectmind" />
            </div>
            <Button variant="outline">{t("settings.testConnection")}</Button>
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
              <Input defaultValue="text-embedding-3-large" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{t("settings.autoEmbed")}</p>
                <p className="text-xs text-muted-foreground">{t("settings.autoEmbed.desc")}</p>
              </div>
              <Switch defaultChecked />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{t("settings.aiImpact")}</p>
                <p className="text-xs text-muted-foreground">{t("settings.aiImpact.desc")}</p>
              </div>
              <Switch defaultChecked />
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
              <Input type="password" defaultValue="dm_live_••••••••••••" />
            </div>
            <Button variant="outline">{t("settings.regenKey")}</Button>
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
                <Switch defaultChecked={i !== 2} />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}