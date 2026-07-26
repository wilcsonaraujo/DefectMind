import { useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { getCurrentUser, type UserResponse } from "@/lib/api";

/**
 * Retorna o token JWT armazenado ou null se não estiver autenticado.
 */
export function getToken(): string | null {
  if (typeof localStorage === "undefined") return null;
  return localStorage.getItem("dm-token");
}

/**
 * Decodifica só o que o JWT de fato carrega: `role` e `exp`.
 * Nome e e-mail NÃO estão no payload do token (ver create_access_token
 * no backend) — para exibição, use useAuth().user, que busca /auth/me.
 * Retorna null se o token não existir ou for inválido.
 */
export function getTokenClaims(): { role: string; exp: number } | null {
  const token = getToken();
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return { role: payload.role ?? "viewer", exp: payload.exp };
  } catch {
    return null;
  }
}

/**
 * True se não houver token, o token for inválido, ou `exp` já tiver
 * passado. `exp` do JWT é em segundos desde a epoch — Date.now() é em ms.
 */
export function isTokenExpired(): boolean {
  const claims = getTokenClaims();
  if (!claims?.exp) return true;
  return Date.now() >= claims.exp * 1000;
}

/**
 * Remove o token do localStorage e redireciona para /login.
 */
export function logout(navigate: ReturnType<typeof useNavigate>) {
  localStorage.removeItem("dm-token");
  navigate({ to: "/login" });
}

/**
 * Hook principal de autenticação. Busca o usuário real (nome, e-mail,
 * role) via GET /auth/me — não decodifica isso do JWT, porque o token
 * não carrega esses campos.
 */
export function useAuth() {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!getToken() || isTokenExpired()) {
      localStorage.removeItem("dm-token");
      setUser(null);
      setIsLoading(false);
      return;
    }
    getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setIsLoading(false));
  }, []);

  const handleLogout = () => {
    logout(navigate);
    setUser(null);
  };

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    logout: handleLogout,
  };
}
