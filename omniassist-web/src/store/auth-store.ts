// Persisted auth state — tokens, current user and organization.
// The access token is read by the API client (lib/api.ts) for the bearer header
// and rotated by the refresh flow.

import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface AuthUser {
  id: string;
  email: string;
  fullName: string;
  avatarUrl?: string | null;
  title?: string | null;
}

export interface AuthOrg {
  id: string;
  name: string;
  slug: string;
  role: string;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  org: AuthOrg | null;
  isAuthenticated: boolean;
  setSession: (args: {
    accessToken: string;
    refreshToken: string;
    user: AuthUser;
    org: AuthOrg;
  }) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      org: null,
      isAuthenticated: false,
      setSession: ({ accessToken, refreshToken, user, org }) =>
        set({ accessToken, refreshToken, user, org, isAuthenticated: true }),
      setTokens: (accessToken, refreshToken) => set({ accessToken, refreshToken }),
      clear: () =>
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          org: null,
          isAuthenticated: false,
        }),
    }),
    { name: "omniassist-auth" }
  )
);
