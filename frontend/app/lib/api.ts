/**
 * Authenticated fetch helper.
 * Pass `getToken` from Clerk's `useAuth()` to inject the Authorization header.
 */
export async function apiFetch(
  url: string,
  options: RequestInit = {},
  getToken?: () => Promise<string | null>
): Promise<Response> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (getToken) {
    const token = await getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  return fetch(url, { ...options, headers });
}
