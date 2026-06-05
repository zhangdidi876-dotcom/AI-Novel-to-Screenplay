const BASE = "/api";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // ── 文件上传 ──
  uploadFile: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
    return res.json();
  },

  uploadText: async (text: string) => {
    const form = new FormData();
    form.append("text", text);
    const res = await fetch(`${BASE}/upload/text`, { method: "POST", body: form });
    return res.json();
  },

  // ── AI 转换 ──
  extractCharacters: (text: string, modelIndex = 0) =>
    request<{ characters: unknown[] }>("/extract/characters", {
      method: "POST",
      body: JSON.stringify({ text, model_index: modelIndex }),
    }),

  extractScenes: (text: string, modelIndex = 0) =>
    request<{ scenes: unknown[] }>("/extract/scenes", {
      method: "POST",
      body: JSON.stringify({ text, model_index: modelIndex }),
    }),

  generateScript: (text: string, modelIndex = 0) =>
    request<{ screenplay: unknown }>("/generate/script", {
      method: "POST",
      body: JSON.stringify({ text, model_index: modelIndex }),
    }),

  // ── 历史记录 ──
  listHistory: () => request<{ history: unknown[] }>("/history"),

  getHistoryDetail: (id: number) => request<unknown>(`/history/${id}`),

  deleteHistory: (id: number) =>
    request<{ status: string }>(`/history/${id}`, { method: "DELETE" }),

  // ── 健康检查 ──
  healthCheck: () => request<{ status: string }>("/health"),
};
