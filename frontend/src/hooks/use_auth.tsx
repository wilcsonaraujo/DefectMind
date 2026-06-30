import { useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";

/**
 * Redireciona para /login se não houver token JWT no localStorage.
 * Use em páginas que exigem autenticação.
 */
export function useRequireAuth() {
  const navigate = useNavigate();
  useEffect(() => {
    const token = localStorage.getItem("dm-token");
    if (!token) {
      navigate({ to: "/login" });
    }
  }, [navigate]);
}

/**
 * Retorna o token JWT armazenado ou null se não estiver autenticado.
 */
export function getToken(): string | null {
  if (typeof localStorage === "undefined") return null;
  return localStorage.getItem("dm-token");
}

/**
 * Decodifica o payload do JWT e retorna nome e e-mail do usuário.
 * Retorna null se o token não existir ou for inválido.
 */
export function getUserFromToken(): { name: string; email: string } | null {
  const token = getToken();
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return {
      email: payload.sub ?? "",
      name: payload.name ?? payload.sub ?? "Usuário",
    };
  } catch {
    return null;
  }
}

/**
 * Remove o token do localStorage e redireciona para /login.
 */
export function logout(navigate: ReturnType<typeof useNavigate>) {
  localStorage.removeItem("dm-token");
  navigate({ to: "/login" });
}