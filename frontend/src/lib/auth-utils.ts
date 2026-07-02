export function getUserFromToken(): { email: string; role: string } | null {
  try {
    const token = localStorage.getItem("dm-token");
    if (!token) return null;
    const payload = JSON.parse(atob(token.split(".")[1]));
    return { email: payload.sub ?? "", role: payload.role ?? "user" };
  } catch {
    return null;
  }
}