import { createFileRoute } from "@tanstack/react-router";
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
import { useEffect, useState } from "react";
import { AlertCircle, Loader2 } from "lucide-react";
import {
  getStories, getRequirements, getTestCases,
  getBugReports, getIncidents, getPostMortems,
} from "@/lib/api";
import { useLang } from "@/lib/i18n";

type ArtifactType = "Story" | "Requirement" | "Test Case" | "Bug" | "Incident" | "Post-Mortem";

interface ArtifactRow {
  id: string;
  type: ArtifactType;
  name: string;
  date: string;
}

const artifactTypeColors: Record<ArtifactType, string> = {
  "Story":      "border-blue-500/40 text-blue-400",
  "Requirement":"border-purple-500/40 text-purple-400",
  "Test Case":  "border-emerald-500/40 text-emerald-400",
  "Bug":        "border-red-500/40 text-red-400",
  "Incident":   "border-orange-500/40 text-orange-400",
  "Post-Mortem":"border-amber-500/40 text-amber-400",
};

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
  const [type, setType] = useState<ArtifactType | "All">("All");
  const [allArtifacts, setAllArtifacts] = useState<ArtifactRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { t } = useLang();

  useEffect(() => {
    Promise.all([
      getStories(),
      getRequirements(),
      getTestCases(),
      getBugReports(),
      getIncidents(),
      getPostMortems(),
    ])
      .then(([stories, reqs, tests, bugs, incidents, postmortems]) => {
        const rows: ArtifactRow[] = [
          ...stories.map((a) => ({ id: a.id, type: "Story" as ArtifactType, name: a.title, date: a.created_at })),
          ...reqs.map((a) => ({ id: a.id, type: "Requirement" as ArtifactType, name: a.title, date: a.created_at })),
          ...tests.map((a) => ({ id: a.id, type: "Test Case" as ArtifactType, name: a.title, date: a.created_at })),
          ...bugs.map((a) => ({ id: a.id, type: "Bug" as ArtifactType, name: a.title, date: a.created_at })),
          ...incidents.map((a) => ({ id: a.id, type: "Incident" as ArtifactType, name: a.title, date: a.created_at })),
          ...postmortems.map((a) => ({ id: a.id, type: "Post-Mortem" as ArtifactType, name: a.title, date: a.created_at })),
        ];
        setAllArtifacts(rows);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const rows = allArtifacts.filter(
    (a) =>
      (type === "All" || a.type === type) &&
      (a.name.toLowerCase().includes(q.toLowerCase()) ||
        a.id.toLowerCase().includes(q.toLowerCase())),
  );

  if (loading) {
    return (
      <AppLayout title={t("artifacts.title")} subtitle={t("artifacts.subtitle")}>
        <div className="flex h-64 items-center justify-center gap-3 text-muted-foreground">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Carregando artefatos…</span>
        </div>
      </AppLayout>
    );
  }

  if (error) {
    return (
      <AppLayout title={t("artifacts.title")} subtitle={t("artifacts.subtitle")}>
        <div className="flex h-64 flex-col items-center justify-center gap-3">
          <AlertCircle className="h-8 w-8 text-destructive" />
          <p className="text-sm text-destructive">{error}</p>
          <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
            Tentar novamente
          </Button>
        </div>
      </AppLayout>
    );
  }
  
  return (
    <AppLayout
      title={t("artifacts.title")}
      subtitle={t("artifacts.subtitle")}
/*       actions={
        <Button>
          <Plus className="h-4 w-4" /> {t("artifacts.new")}
        </Button>
      } */
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