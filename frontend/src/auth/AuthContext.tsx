import React, { createContext, useContext, useMemo, useState } from "react";

import { loginRequest } from "../api/client";

interface AuthContextValue {
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("jwt"));

  const login = async (email: string, password: string) => {
    const data = await loginRequest(email, password);
    setToken(data.access_token);
    localStorage.setItem("jwt", data.access_token);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem("jwt");
  };

  const value = useMemo(() => ({ token, login, logout }), [token]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("AuthContext missing");
  }
  return ctx;
}
