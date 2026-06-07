import { useState, useEffect } from "react";

interface ModelInfo {
  name: string;
  model_name: string;
}

interface Props {
  modelIndex: number;
  onModelChange: (index: number) => void;
}

export default function ModelConfig({ modelIndex, onModelChange }: Props) {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [show, setShow] = useState(false);

  useEffect(() => {
    fetch("/api/models")
      .then((r) => r.json())
      .then((d) => setModels(d.models || []))
      .catch(() => setModels([{ name: "默认模型", model_name: "" }]));
  }, []);

  return (
    <div style={{ padding: "4px 0" }}>
      <div
        onClick={() => setShow(!show)}
        style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          cursor: "pointer", padding: "8px 14px",
          background: "rgba(0,229,255,0.06)", border: "1px solid rgba(0,229,255,0.12)",
          borderRadius: 8, fontSize: 12, color: "var(--cyan)", fontWeight: 500,
          transition: "all 0.2s",
        }}
      >
        <span>🤖 {models[modelIndex]?.name || "默认"}</span>
        <span style={{ color: "var(--text-dim)", fontSize: 10 }}>{show ? "▲" : "▼"}</span>
      </div>
      {show && (
        <div style={{ marginTop: 8 }}>
          {models.map((m, i) => (
            <label
              key={i}
              style={{
                display: "flex", alignItems: "center", gap: 8,
                padding: "8px 14px", cursor: "pointer", borderRadius: 8,
                background: modelIndex === i ? "rgba(0,229,255,0.08)" : "transparent",
                border: modelIndex === i ? "1px solid rgba(0,229,255,0.2)" : "1px solid transparent",
                transition: "all 0.2s",
              }}
            >
              <input
                type="radio" name="model"
                checked={modelIndex === i}
                onChange={() => { onModelChange(i); setShow(false); }}
                style={{ accentColor: "var(--cyan)" }}
              />
              <div>
                <div style={{ fontWeight: 600, fontSize: 13, color: "var(--text)" }}>{m.name}</div>
                <div style={{ fontSize: 11, color: "var(--text-dim)" }}>{m.model_name}</div>
              </div>
            </label>
          ))}
          <p style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 8, paddingLeft: 14 }}>
            💡 在 backend/.env 配置更多模型
          </p>
        </div>
      )}
    </div>
  );
}
