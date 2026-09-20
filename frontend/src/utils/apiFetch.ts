const API_BASE = import.meta.env.VITE_API_URL;

export const AUTH_UNAUTHORIZED_EVENT = "auth:unauthorized";

/**
 * Wrapper around fetch for authenticated API requests.
 */
export async function apiFetch(
  path: string,
  init: RequestInit = {}
): Promise<Response> {
  const token = localStorage.getItem("access_token");

  const headers = new Headers(init.headers);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  if (response.status === 401) {
    window.dispatchEvent(new Event(AUTH_UNAUTHORIZED_EVENT));

    window.location.href = "/login";
  }

  return response;
}

/**
 * Fetch using the configured API base URL.
 * This is kept as a separate helper for code that needs
 * the same authenticated fetch behaviour.
 */

