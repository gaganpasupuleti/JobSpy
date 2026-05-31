import { useMemo } from "react";

const SESSION_KEY = "jobboard_session_id";
const SAVED_KEY = "jobboard_saved_jobs";

function randomId() {
  return crypto.randomUUID?.() || `sess-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function getSessionId() {
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = randomId();
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export function getSavedJobIds() {
  try {
    return JSON.parse(localStorage.getItem(SAVED_KEY) || "[]");
  } catch {
    return [];
  }
}

export function addSavedJobId(id) {
  const saved = getSavedJobIds();
  if (!saved.includes(id)) {
    saved.unshift(id);
    localStorage.setItem(SAVED_KEY, JSON.stringify(saved));
  }
}

export function removeSavedJobId(id) {
  const saved = getSavedJobIds().filter((x) => x !== id);
  localStorage.setItem(SAVED_KEY, JSON.stringify(saved));
}

export function useSession() {
  return useMemo(() => ({ sessionId: getSessionId() }), []);
}
