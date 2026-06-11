// Typed fetch client for the omniassist-api backend.
//
// - Base URL from NEXT_PUBLIC_API_URL. When unset, `apiConfigured()` is false and
//   the React Query hooks fall back to local mock data, so the app runs without a
//   backend (demo mode).
// - Sends the bearer access token from the auth store and transparently refreshes
//   it once on a 401.
// - Backend success responses are sometimes wrapped in `{ data, error }` and
//   sometimes returned raw — `unwrap()` handles both. Errors are `{ error: { code,
//   message } }`.

import { useAuthStore } from "@/store/auth-store";

const BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";
const PREFIX = "/api/v1";

export function apiConfigured(): boolean {
  return BASE.length > 0;
}

export class ApiError extends Error {
  code: string;
  status: number;
  constructor(message: string, code: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

function unwrap<T>(body: unknown): T {
  if (
    body &&
    typeof body === "object" &&
    "data" in body &&
    "error" in (body as Record<string, unknown>)
  ) {
    return (body as { data: T }).data;
  }
  return body as T;
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  auth?: boolean; // attach bearer token (default true)
  signal?: AbortSignal;
}

async function raw(path: string, opts: RequestOptions): Promise<Response> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (opts.auth !== false) {
    const token = useAuthStore.getState().accessToken;
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }
  return fetch(`${BASE}${PREFIX}${path}`, {
    method: opts.method ?? "GET",
    headers,
    body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    signal: opts.signal,
  });
}

export async function apiFetch<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  if (!apiConfigured()) {
    throw new ApiError("API not configured", "API_NOT_CONFIGURED", 0);
  }

  let res = await raw(path, opts);

  // One transparent refresh attempt on expiry.
  if (res.status === 401 && opts.auth !== false) {
    const refreshed = await tryRefresh();
    if (refreshed) res = await raw(path, opts);
  }

  if (res.status === 204) return undefined as T;

  let body: unknown = null;
  try {
    body = await res.json();
  } catch {
    /* empty body */
  }

  if (!res.ok) {
    const err = (body as { error?: { code?: string; message?: string } })?.error;
    if (res.status === 401) useAuthStore.getState().clear();
    throw new ApiError(
      err?.message ?? `Request failed (${res.status})`,
      err?.code ?? "REQUEST_FAILED",
      res.status
    );
  }

  return unwrap<T>(body);
}

let refreshing: Promise<boolean> | null = null;

async function tryRefresh(): Promise<boolean> {
  const { refreshToken, setTokens, clear } = useAuthStore.getState();
  if (!refreshToken) return false;
  if (refreshing) return refreshing;

  refreshing = (async () => {
    try {
      const res = await raw("/auth/refresh", {
        method: "POST",
        body: { refresh_token: refreshToken },
        auth: false,
      });
      if (!res.ok) {
        clear();
        return false;
      }
      const tokens = unwrap<{ access_token: string; refresh_token: string }>(
        await res.json()
      );
      setTokens(tokens.access_token, tokens.refresh_token);
      return true;
    } catch {
      clear();
      return false;
    } finally {
      refreshing = null;
    }
  })();

  return refreshing;
}
