import { type ReactNode, useEffect, useState } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import {
  LayoutDashboard,
  Package,
  Search,
  Share2,
  GitCompareArrows,
  FlaskConical,
  Users,
  Menu,
  X,
  LogOut,
  Languages,
  Bell,
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { useLang } from "@/lib/i18n";
import { useAuth } from "@/hooks/use-auth";
import { getUserFromToken } from "@/lib/auth-utils";
import { getHealthStatus, type HealthResponse } from "@/lib/api";

const navItems = [
  { key: "nav.dashboard",  icon: LayoutDashboard, to: "/"           },
  { key: "nav.artifacts",  icon: Package,         to: "/artifacts"  },
  { key: "nav.search",     icon: Search,          to: "/search"     },
  { key: "nav.graph",      icon: Share2,          to: "/graph"      },
  { key: "nav.impact",     icon: GitCompareArrows,to: "/impact"     },
  { key: "nav.dataForge",  icon: FlaskConical,    to: "/data-forge" },
  { key: "nav.users",      icon: Users,           to: "/users"      },
] as const;

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const { t } = useLang();
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-16 items-center gap-2 border-b border-sidebar-border px-4">
        <div className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-primary-foreground">
          <Share2 className="h-4 w-4" />
        </div>
        <span className="font-semibold tracking-tight">DefectMind</span>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {navItems.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-sidebar-foreground/70 transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground [&.active]:bg-sidebar-accent [&.active]:font-medium [&.active]:text-sidebar-foreground"
          >
            <item.icon className="h-4 w-4 shrink-0" />
            {t(item.key)}
          </Link>
        ))}
      </nav>
      <UserFooter />
    </div>
  );
}

function UserFooter() {
  const { t } = useLang();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const user = getUserFromToken();
  const displayName = user?.name ?? "Usuário";
  const displayEmail = user?.email ?? "";
  const initials = displayName
    .split(" ")
    .map((n: string) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
  return (
    <div className="border-t border-sidebar-border p-3">
      <div className="flex items-center gap-2">
        <Avatar className="h-8 w-8 shrink-0">
          <AvatarFallback className="bg-primary/20 text-xs text-primary">{initials}</AvatarFallback>
        </Avatar>
        <div className="min-w-0 flex-1">
          <p className="truncate text-xs font-medium">{displayName}</p>
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
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const { t, lang, setLang } = useLang();

  // Dados do usuário para o avatar do header
  const user = getUserFromToken();
  const initials = (user?.name ?? "U")
    .split(" ")
    .map((n: string) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  useEffect(() => {
    getHealthStatus()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  const envValue = health?.environment ?? "—";
  const versionValue = health?.version ?? "—";
  const neo4jValue = health
    ? health.neo4j === "connected"
      ? t("status.connected")
      : t("status.disconnected")
    : "—";
  const neo4jColor =
    health?.neo4j === "connected" ? "bg-success" : "bg-destructive";

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
              <StatusBadge
                label={t("status.environment")}
                value={envValue}
                color={envValue === "production" ? "bg-destructive" : "bg-success"}
              />
              <StatusBadge
                label={t("status.version")}
                value={versionValue}
                color="bg-primary"
              />
              <StatusBadge
                label={t("status.neo4j")}
                value={neo4jValue}
                color={neo4jColor}
              />
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
