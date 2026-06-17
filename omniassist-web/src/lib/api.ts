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

/** Confirmed auth failure: clear the dead session and bounce to login so the
 *  user re-authenticates instead of seeing cryptic "missing bearer token" errors. */
function onUnauthorized() {
  useAuthStore.getState().clear();
  if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
    window.location.href = "/login?expired=1";
  }
}

export async function apiFetch<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  if (!apiConfigured()) {
    throw new ApiError("API not configured", "API_NOT_CONFIGURED", 0);
  }

  const sentToken = opts.auth !== false ? useAuthStore.getState().accessToken : null;
  let res = await raw(path, opts);

  // One transparent refresh attempt on expiry. If a concurrent request already
  // rotated the token, skip the refresh and just replay with the new one.
  if (res.status === 401 && opts.auth !== false) {
    const current = useAuthStore.getState().accessToken;
    const refreshed = current && current !== sentToken ? true : await tryRefresh();
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
    if (res.status === 401) onUnauthorized();
    throw new ApiError(
      err?.message ?? `Request failed (${res.status})`,
      err?.code ?? "REQUEST_FAILED",
      res.status
    );
  }

  return unwrap<T>(body);
}

/** Multipart upload (FormData). Lets the browser set the multipart boundary;
 *  attaches the bearer token and retries once on a 401, like `apiFetch`. */
export async function apiUpload<T>(path: string, form: FormData): Promise<T> {
  if (!apiConfigured()) {
    throw new ApiError("API not configured", "API_NOT_CONFIGURED", 0);
  }
  const send = async (): Promise<Response> => {
    const headers: Record<string, string> = {};
    const token = useAuthStore.getState().accessToken;
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return fetch(`${BASE}${PREFIX}${path}`, { method: "POST", headers, body: form });
  };

  const sentToken = useAuthStore.getState().accessToken;
  let res = await send();
  if (res.status === 401) {
    const current = useAuthStore.getState().accessToken;
    const refreshed = current && current !== sentToken ? true : await tryRefresh();
    if (refreshed) res = await send();
  }

  let body: unknown = null;
  try {
    body = await res.json();
  } catch {
    /* empty body */
  }
  if (!res.ok) {
    const err = (body as { error?: { code?: string; message?: string } })?.error;
    if (res.status === 401) onUnauthorized();
    throw new ApiError(
      err?.message ?? `Upload failed (${res.status})`,
      err?.code ?? "UPLOAD_FAILED",
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
