import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Search, Plus, Link2 } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { artifacts, artifactTypeColors, type ArtifactType } from "@/lib/mock-data";
import { useLang } from "@/lib/i18n";

export const Route = createFileRoute("/artifacts")({
  head: () => ({
    meta: [
      { title: "Artefatos — DefectMind" },
      { name: "description", content: "Navegue por todos os artefatos de QA e suas relações." },
    ],
  }),
  component: ArtifactsPage,
});

const types: (ArtifactType | "All")[] = [
  "All",
  "Story",
  "Requirement",
  "Test Case",
  "Bug",
  "Incident",
  "Post-Mortem",
];

function ArtifactsPage() {
  const [q, setQ] = useState("");
  const [type, setType] = useState<(typeof types)[number]>("All");
  const { t } = useLang();

  const rows = useMemo(
    () =>
      artifacts.filter(
        (a) =>
          (type === "All" || a.type === type) &&
          (a.name.toLowerCase().includes(q.toLowerCase()) ||
            a.id.toLowerCase().includes(q.toLowerCase())),
      ),
    [q, type],
  );

  return (
    <AppLayout
      title={t("artifacts.title")}
      subtitle={t("artifacts.subtitle")}
      actions={
        <Button>
          <Plus className="h-4 w-4" /> {t("artifacts.new")}
        </Button>
      }
    >
      <Card>
        <CardContent className="p-4">
          <div className="grid gap-2 sm:grid-cols-[minmax(0,1fr)_180px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder={t("artifacts.filterPlaceholder")}
                className="pl-9"
              />
            </div>
            <Select value={type} onValueChange={(v) => setType(v as typeof type)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {types.map((opt) => (
                  <SelectItem key={opt} value={opt}>
                    {opt === "All" ? t("artifacts.all") : opt}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="mt-4 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t("artifacts.col.type")}</TableHead>
                  <TableHead>{t("artifacts.col.id")}</TableHead>
                  <TableHead>{t("artifacts.col.name")}</TableHead>
                  <TableHead>{t("artifacts.col.date")}</TableHead>
                  <TableHead className="text-right">{t("artifacts.col.relationships")}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((a) => (
                  <TableRow key={a.id} className="cursor-pointer">
                    <TableCell>
                      <Badge variant="outline" className={artifactTypeColors[a.type]}>
                        {a.type}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs text-muted-foreground">{a.id}</TableCell>
                    <TableCell className="font-medium">{a.name}</TableCell>
                    <TableCell className="text-muted-foreground">{a.date}</TableCell>
                    <TableCell className="text-right">
                      <span className="inline-flex items-center gap-1 text-muted-foreground">
                        <Link2 className="h-3.5 w-3.5" /> {a.relationships}
                      </span>
                    </TableCell>
                  </TableRow>
                ))}
                {rows.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="py-10 text-center text-muted-foreground">
                      {t("artifacts.empty")}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </AppLayout>
  );
}