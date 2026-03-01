export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
export const API_BASE = API_URL.replace(/\/api\/?$/, "");

async function request<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const resp = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(text || resp.statusText);
  }
  return resp.json();
}

export interface Classification {
  id: string;
  status: string;
  summary?: string | null;
  artifact_type?: string | null;
  civilization?: string | null;
  age_range?: string | null;
  confidence?: number | null;
  provider?: string;
}

export interface ArtifactListItem {
  id: string;
  artifact_id: string;
  timestamp: string;
  location_approx?: string | null;
  latest_classification?: Classification | null;
}

export interface ArtifactDetail {
  id: string;
  artifact_id: string;
  timestamp: string;
  location_approx?: string | null;
  measure_length_cm: number;
  measure_width_cm: number;
  measure_height_cm: number;
  additional_info?: Record<string, unknown> | null;
  images: { id: string; url: string }[];
  latest_classification?: Classification | null;
}

export interface LoginResponse {
  access_token: string;
}

export async function loginRequest(email: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
}

export async function getArtifacts(params: Record<string, string | number | undefined>) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      qs.append(key, String(value));
    }
  });
  const suffix = qs.toString() ? `?${qs.toString()}` : "";
  return request<ArtifactListItem[]>(`/artifacts${suffix}`);
}

export async function getArtifact(id: string) {
  return request<ArtifactDetail>(`/artifacts/${id}`);
}

export async function createArtifact(payload: Record<string, unknown>, token: string, files?: File[]) {
  if (files && files.length > 0) {
    const form = new FormData();
    form.append("metadata", JSON.stringify(payload));
    files.forEach((file) => form.append("files", file));
    return request<ArtifactDetail>("/artifacts", { method: "POST", body: form }, token);
  }
  return request<ArtifactDetail>("/artifacts", { method: "POST", body: JSON.stringify(payload) }, token);
}

export async function updateArtifact(id: string, payload: Record<string, unknown>, token: string) {
  return request<ArtifactDetail>(`/artifacts/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token);
}

export async function overrideClassification(
  id: string,
  payload: Record<string, unknown>,
  token: string
) {
  return request<Classification>(
    `/artifacts/${id}/classification`,
    { method: "PUT", body: JSON.stringify(payload) },
    token
  );
}

export async function classifyArtifact(id: string, token: string) {
  return request<Classification>(`/artifacts/${id}/classify`, { method: "POST" }, token);
}
