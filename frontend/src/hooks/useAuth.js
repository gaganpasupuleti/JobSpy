import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";

const TOKEN_KEY = "jobboard_auth_token";
const USER_KEY = "jobboard_auth_user";

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

export function getAuthUser() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function persistAuth(token, student) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(student));
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function useAuth() {
  const [user, setUser] = useState(getAuthUser);
  const [loading, setLoading] = useState(false);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    try {
      const data = await api.login(email, password);
      persistAuth(data.access_token, data.student);
      setUser(data.student);
      return data.student;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    clearAuth();
    setUser(null);
  }, []);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) return;
    api
      .getMe(token)
      .then((student) => {
        setUser(student);
        localStorage.setItem(USER_KEY, JSON.stringify(student));
      })
      .catch(() => logout());
  }, [logout]);

  return {
    user,
    token: getAuthToken(),
    isLoggedIn: Boolean(user && getAuthToken()),
    loading,
    login,
    logout,
  };
}
