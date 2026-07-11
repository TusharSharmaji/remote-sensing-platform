import {
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { AuthContext } from "./AuthContext";

import {
  saveTokens,
  clearTokens,
} from "../storage/tokenStorage";

import type { AuthUser } from "../types/auth";

interface AuthProviderProps {
  children: ReactNode;
}

function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] =
    useState<AuthUser | null>(null);

  function login(
    user: AuthUser,
    accessToken: string,
    refreshToken: string,
  ) {
    saveTokens(accessToken, refreshToken);
    setUser(user);
  }

  function logout() {
    clearTokens();
    setUser(null);
  }

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: user !== null,
      login,
      logout,
    }),
    [user],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;