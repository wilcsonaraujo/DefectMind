import { createFileRoute } from "@tanstack/react-router";
import { UserPlus } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { users } from "@/lib/mock-data";
import { useLang } from "@/lib/i18n";

export const Route = createFileRoute("/users")({
  head: () => ({
    meta: [
      { title: "Usuários — DefectMind" },
      { name: "description", content: "Gerencie membros da equipe e acessos no DefectMind." },
    ],
  }),
  component: UsersPage,
});

const statusColor: Record<string, string> = {
  Ativo: "bg-success/15 text-success border-success/30",
  Convidado: "bg-chart-1/15 text-chart-1 border-chart-1/30",
  Inativo: "bg-muted text-muted-foreground border-border",
};

function UsersPage() {
  const { t, tt } = useLang();
  return (
    <AppLayout
      title={t("users.title")}
      subtitle={t("users.subtitle")}
      actions={
        <Button>
          <UserPlus className="h-4 w-4" /> {t("users.invite")}
        </Button>
      }
    >
      <Card>
        <CardContent className="overflow-x-auto p-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("users.col.member")}</TableHead>
                <TableHead>{t("users.col.role")}</TableHead>
                <TableHead>{t("users.col.team")}</TableHead>
                <TableHead>{t("users.col.status")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((u) => (
                <TableRow key={u.email}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-secondary text-xs">
                          {u.name.split(" ").map((n) => n[0]).join("").slice(0, 2)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="min-w-0">
                        <p className="truncate font-medium">{u.name}</p>
                        <p className="truncate text-xs text-muted-foreground">{u.email}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{tt(u.role)}</TableCell>
                  <TableCell className="text-muted-foreground">{tt(u.team)}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className={statusColor[u.status]}>
                      {tt(u.status)}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </AppLayout>
  );
}