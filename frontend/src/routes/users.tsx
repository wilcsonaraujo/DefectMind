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
import { useEffect, useState } from "react";
import { AlertCircle, Loader2 } from "lucide-react";
import { getUsers, type UserResponse } from "@/lib/api";
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
  const [userList, setUserList] = useState<UserResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { t } = useLang();

  useEffect(() => {
    getUsers()
      .then(setUserList)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <AppLayout title={t("users.title")} subtitle={t("users.subtitle")}>
        <div className="flex h-64 items-center justify-center gap-3 text-muted-foreground">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Carregando usuários…</span>
        </div>
      </AppLayout>
    );
  }

  if (error) {
    return (
      <AppLayout title={t("users.title")} subtitle={t("users.subtitle")}>
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
      title={t("users.title")}
      subtitle={t("users.subtitle")}
      /* actions={
        <Button>
          <UserPlus className="h-4 w-4" /> {t("users.invite")}
        </Button>
      } */
    >
      <Card>
        <CardContent className="overflow-x-auto p-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("users.col.member")}</TableHead>
                <TableHead>{t("users.col.role")}</TableHead>
                <TableHead>{t("users.col.status")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {userList.map((u) => (
                <TableRow key={u.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-secondary text-xs">
                          {(u.full_name ?? u.email)
                            .split(" ")
                            .map((n) => n[0])
                            .join("")
                            .slice(0, 2)
                            .toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div className="min-w-0">
                        <p className="truncate font-medium">{u.full_name ?? "—"}</p>
                        <p className="truncate text-xs text-muted-foreground">{u.email}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{u.role}</TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        u.is_active
                          ? "bg-success/15 text-success border-success/30"
                          : "bg-muted text-muted-foreground border-border"
                      }
                    >
                      {u.is_active ? "Ativo" : "Inativo"}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
              {userList.length === 0 && (
                <TableRow>
                  <TableCell colSpan={3} className="py-10 text-center text-muted-foreground">
                    Nenhum usuário encontrado.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </AppLayout>
  );
}
