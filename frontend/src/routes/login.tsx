import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { BrainCircuit, Mail, Lock, Loader2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { useLang } from "@/lib/i18n";
import cloudsBg from "@/assets/login-clouds.jpg";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Entrar — DefectMind" },
      { name: "description", content: "Acesse o DefectMind, a plataforma de inteligência para QA." },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const { t } = useLang();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError(t("login.error"));
      return;
    }
    setError(null);
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      navigate({ to: "/" });
    }, 800);
  };

  return (
    <div className="grid min-h-screen w-full bg-background text-foreground lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden flex-col justify-between overflow-hidden border-r border-sidebar-border bg-sidebar p-12 lg:flex">
        <img
          src={cloudsBg}
          alt=""
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 h-full w-full object-cover opacity-40"
        />
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "linear-gradient(180deg, color-mix(in oklch, var(--sidebar) 55%, transparent), color-mix(in oklch, var(--sidebar) 85%, transparent))",
          }}
        />
        <div
          className="pointer-events-none absolute inset-0 opacity-60"
          style={{
            background:
              "radial-gradient(60% 50% at 20% 10%, color-mix(in oklch, var(--primary) 25%, transparent), transparent), radial-gradient(50% 40% at 90% 90%, color-mix(in oklch, var(--primary) 18%, transparent), transparent)",
          }}
        />
        <div className="relative flex items-center gap-2.5">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary text-primary-foreground">
            <BrainCircuit className="h-5 w-5" />
          </div>
          <div>
            <p className="text-base font-bold tracking-tight text-sidebar-foreground">DefectMind</p>
            <p className="text-[11px] text-muted-foreground">{t("tagline")}</p>
          </div>
        </div>
        <div className="relative max-w-sm">
          <h2 className="text-3xl font-bold leading-tight tracking-tight text-sidebar-foreground">
            {t("login.welcome")}
          </h2>
          <p className="mt-3 text-sm text-muted-foreground">{t("login.tagline")}</p>
        </div>
        <div className="relative flex items-center gap-2 text-[11px] text-muted-foreground">
          <span className="h-1.5 w-1.5 rounded-full bg-success" /> Neo4j · {t("status.connected")} · v0.1.0
        </div>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2.5 lg:hidden">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary text-primary-foreground">
              <BrainCircuit className="h-5 w-5" />
            </div>
            <p className="text-base font-bold tracking-tight">DefectMind</p>
          </div>

          <h1 className="text-2xl font-bold tracking-tight">{t("login.welcome")}</h1>
          <p className="mt-1 text-sm text-muted-foreground">{t("login.subtitle")}</p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email">{t("login.email")}</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t("login.emailPlaceholder")}
                  className="pl-9"
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">{t("login.password")}</Label>
                <a href="#" className="text-xs font-medium text-primary hover:underline">
                  {t("login.forgot")}
                </a>
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={t("login.passwordPlaceholder")}
                  className="pl-9"
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Checkbox id="remember" />
              <Label htmlFor="remember" className="text-sm font-normal text-muted-foreground">
                {t("login.remember")}
              </Label>
            </div>

            {error && (
              <p className="rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </p>
            )}

            <Button type="submit" className="w-full gap-2" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" /> {t("login.submitting")}
                </>
              ) : (
                <>
                  {t("login.submit")} <ArrowRight className="h-4 w-4" />
                </>
              )}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            {t("login.noAccount")}{" "}
            <a href="#" className="font-medium text-primary hover:underline">
              {t("login.requestAccess")}
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}