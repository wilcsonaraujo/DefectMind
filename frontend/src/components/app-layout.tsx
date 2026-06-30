import { Link, useRouterState, useNavigate } from "@tanstack/react-router";
import { useState, type ReactNode } from "react";
import {
  LayoutDashboard,
  Search,
  GitCompareArrows,
  Share2,
  FlaskConical,
  Boxes,
  Users,
  Settings,
  Server,
  Bell,
  Menu,
  X,
  BrainCircuit,
  LogOut,
  Languages,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useLang } from "@/lib/i18n";
import { getUserFromToken, logout } from "@/hooks/use-auth";

const navMain = [
  { to: "/", key: "nav.dashboard", subKey: "nav.dashboard.sub", icon: LayoutDashboard },
  { to: "/search", key: "nav.search", subKey: "nav.search.sub", icon: Search },
  { to: "/impact", key: "nav.impact", subKey: "nav.impact.sub", icon: GitCompareArrows },
  { to: "/graph", key: "nav.graph", subKey: "nav.graph.sub", icon: Share2 },
  { to: "/data-forge", key: "nav.dataForge", subKey: "nav.dataForge.sub", icon: FlaskConical },
  { to: "/artifacts", key: "nav.artifacts", subKey: "nav.artifacts.sub", icon: Boxes },
] as const;

const navConfig = [
  { to: "/users", key: "nav.users", icon: Users },
  { to: "/settings", key: "nav.settings", icon: Settings },
  { to: "/environments", key: "nav.environments", icon: Server },
] as const;

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const navigate = useNavigate();
  const { t } = useLang();
  const isActive = (to: string) => (to === "/" ? pathname === "/" : pathname.startsWith(to));

  // Extrair dados do usuário logado a partir do JWT
  const user = getUserFromToken();
  const displayName = user?.name ?? "Usuário";
  const displayEmail = user?.email ?? "";
  const initials = displayName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="flex h-full flex-col">
      <div className="flex h-20 items-center gap-2.5 px-5">
        <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground">
          <BrainCircuit className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="truncate text-base font-bold tracking-tight text-sidebar-foreground">DefectMind</p>
          <p className="truncate text-[11px] text-muted-foreground">{t("tagline")}</p>
        </div>
      </div>
      <nav className="flex-1 overflow-y-auto px-3 py-2">
        <p className="px-3 pb-2 pt-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
          {t("nav.navigation")}
        </p>
        <div className="space-y-1">
          {navMain.map((item) => {
            const active = isActive(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={onNavigate}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 transition-colors",
                  active
                    ? "bg-primary/15 text-sidebar-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-sidebar-foreground",
                )}
              >
                <item.icon className={cn("h-4 w-4 shrink-0", active && "text-primary")} />
                <span className="min-w-0">
                  <span className={cn("block truncate text-sm font-medium", active && "text-sidebar-foreground")}>
                    {t(item.key)}
                  </span>
                  <span className="block truncate text-[11px] text-muted-foreground">{t(item.subKey)}</span>
                </span>
              </Link>
            );
          })}
        </div>
        <p className="px-3 pb-2 pt-5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
          {t("nav.config")}
        </p>
        <div className="space-y-1">
          {navConfig.map((item) => {
            const active = isActive(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={onNavigate}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-primary/15 text-sidebar-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-sidebar-foreground",
                )}
              >
                <item.icon className={cn("h-4 w-4 shrink-0", active && "text-primary")} />
                <span className="truncate">{t(item.key)}</span>
              </Link>
            );
          })}
        </div>
      </nav>
      {/* Footer do sidebar: dados do usuário + botão de logout */}
      <div className="border-t border-sidebar-border p-3">
        <div className="flex items-center gap-3 rounded-lg px-2 py-2">
          <Avatar className="h-8 w-8">
            <AvatarFallback className="bg-primary/20 text-xs text-primary">{initials}</AvatarFallback>
          </Avatar>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-sidebar-foreground">{displayName}</p>
            <p className="truncate text-[11px] text-muted-foreground">{displayEmail}</p>
          </div>
          <button
            onClick={() => logout(navigate)}
            title={t("nav.logout")}
            className="shrink-0 rounded-md p-1 text-muted-foreground transition-colors hover:bg-sidebar-accent/60 hover:text-sidebar-foreground"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="hidden rounded-lg border border-border bg-card px-3 py-1.5 lg:block">
      <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="flex items-center gap-1.5 text-xs font-medium">
        <span className={cn("h-1.5 w-1.5 rounded-full", color)} /> {value}
      </p>
    </div>
  );
}

export function AppLayout({
  title,
  subtitle,
  actions,
  children,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const { t, lang, setLang } = useLang();

  // Dados do usuário para o avatar do header
  const user = getUserFromToken();
  const initials = (user?.name ?? "U")
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="min-h-screen w-full bg-background text-foreground">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-sidebar-border bg-sidebar lg:block">
        <SidebarContent />
      </aside>
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-64 border-r border-sidebar-border bg-sidebar">
            <button
              className="absolute right-3 top-4 text-muted-foreground"
              onClick={() => setOpen(false)}
            >
              <X className="h-5 w-5" />
            </button>
            <SidebarContent onNavigate={() => setOpen(false)} />
          </aside>
        </div>
      )}
      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 border-b border-border bg-background/80 backdrop-blur">
          <div className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 px-4 py-3 sm:px-6">
            <button
              className="grid h-9 w-9 place-items-center rounded-lg border border-border text-muted-foreground lg:hidden"
              onClick={() => setOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="min-w-0" />
            <div className="flex items-center justify-end gap-2">
              <StatusBadge label={t("status.environment")} value="DEV" color="bg-success" />
              <StatusBadge label={t("status.version")} value="v0.1.0" color="bg-primary" />
              <StatusBadge label={t("status.neo4j")} value={t("status.connected")} color="bg-success" />
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="gap-1.5">
                    <Languages className="h-4 w-4" />
                    <span className="text-xs font-medium uppercase">{lang}</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setLang("pt")}>
                    🇧🇷 Português {lang === "pt" && "✓"}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setLang("en")}>
                    🇺🇸 English {lang === "en" && "✓"}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
              <Button variant="outline" size="icon" className="relative">
                <Bell className="h-4 w-4" />
                <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-primary" />
              </Button>
              <Avatar className="h-9 w-9">
                <AvatarFallback className="bg-primary/20 text-xs text-primary">{initials}</AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>
        <main className="px-4 py-6 sm:px-6 lg:px-8">
          <div className="mb-6 grid grid-cols-[minmax(0,1fr)_auto] items-end gap-4">
            <div className="min-w-0">
              <h1 className="truncate text-2xl font-bold tracking-tight">{title}</h1>
              {subtitle && <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>}
            </div>
            {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
          </div>
          {children}
        </main>
      </div>
    </div>
  );
}