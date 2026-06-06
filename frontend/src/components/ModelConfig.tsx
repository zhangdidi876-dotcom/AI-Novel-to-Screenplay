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
    <div style={{ padding: "8px 0" }}>
      <div
        onClick={() => setShow(!show)}
        style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          cursor: "pointer", padding: "8px 12px", background: "#f8f9fa",
          borderRadius: 6, fontSize: 13,
        }}
      >
        <span>🤖 {models[modelIndex]?.name || "默认"}</span>
        <span style={{ color: "#999" }}>{show ? "▲" : "▼"}</span>
      </div>
      {show && (
        <div style={{ marginTop: 8 }}>
          {models.map((m, i) => (
            <label
              key={i}
              style={{
                display: "flex", alignItems: "center", gap: 8,
                padding: "8px 12px", cursor: "pointer", borderRadius: 4,
                background: modelIndex === i ? "#e8f0fe" : "transparent",
              }}
            >
              <input
                type="radio"
                name="model"
                checked={modelIndex === i}
                onChange={() => { onModelChange(i); setShow(false); }}
              />
              <div>
                <div style={{ fontWeight: 600, fontSize: 13 }}>{m.name}</div>
                <div style={{ fontSize: 11, color: "#999" }}>{m.model_name}</div>
              </div>
            </label>
          ))}
          <p style={{ fontSize: 11, color: "#999", marginTop: 8 }}>💡 在 backend/.env 配置更多模型</p>
        </div>
      )}
    </div>
  );
}
