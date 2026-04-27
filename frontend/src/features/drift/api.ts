import type { DriftHistoryResponse, DriftStatusResponse } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchLatestDriftReport(): Promise<DriftStatusResponse> {
  return fetchJson<DriftStatusResponse>("/api/drift/latest");
}

export async function fetchDriftHistory(
  limit = 30,
): Promise<DriftHistoryResponse> {
  return fetchJson<DriftHistoryResponse>(`/api/drift/history?limit=${limit}`);
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}
