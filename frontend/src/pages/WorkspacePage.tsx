import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import type { Character, Scene, Screenplay, StepStatus } from "../types";

type StepKey = "input" | "characters" | "scenes" | "script" | "export";

interface Step {
  key: StepKey;
  label: string;
  icon: string;
}

const STEPS: Step[] = [
  { key: "input", label: "章节预览", icon: "📖" },
  { key: "characters", label: "角色提取", icon: "👤" },
  { key: "scenes", label: "场景拆分", icon: "🎬" },
  { key: "script", label: "剧本预览", icon: "📝" },
  { key: "export", label: "导出 YAML", icon: "📄" },
];

const TIME_LABELS: Record<string, string> = {
  day: "☀️ 日", night: "🌙 夜", dawn: "🌅 清晨", dusk: "🌆 黄昏",
  morning: "🌤 上午", afternoon: "☀️ 下午", evening: "🌇 傍晚",
  continuous: "⟳ 连续", later: "⏱ 稍后", same: "⇉ 同时",
};

export default function WorkspacePage() {
  const navigate = useNavigate();

  const [chapters, setChapters] = useState("");
  const [currentStep, setCurrentStep] = useState<StepKey>("input");
  const [stepStatus, setStepStatus] = useState<Record<string, StepStatus>>({
    input: "done", characters: "idle", scenes: "idle", script: "idle", export: "idle",
  });

  const [characters, setCharacters] = useState<Character[]>([]);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [screenplay, setScreenplay] = useState<Screenplay | null>(null);
  const [yamlOutput, setYamlOutput] = useState("");
  const [error, setError] = useState("");
  const [toast, setToast] = useState<{ type: "success" | "error"; msg: string } | null>(null);

  useEffect(() => {
    const text = sessionStorage.getItem("chapters_text");
    if (!text) { navigate("/"); return; }
    setChapters(text);
  }, [navigate]);

  const showToast = useCallback((type: "success" | "error", msg: string) => {
    setToast({ type, msg });
    setTimeout(() => setToast(null), 3500);
  }, []);

  // ── 一键全流程 ──
  const handleFullConvert = async () => {
    setCurrentStep("characters");
    setStepStatus((s) => ({ ...s, characters: "loading", scenes: "idle", script: "idle", export: "idle" }));
    setError("");
    try {
      const res = await fetch("/api/convert/full", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: chapters, model_index: 0 }),
      });
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || "请求失败"); }
      const data = await res.json();
      const sp = data.screenplay as Screenplay;
      setScreenplay(sp);
      if (sp.characters) setCharacters(sp.characters);
      if (sp.scenes) setScenes(sp.scenes);
      setStepStatus((s) => ({ ...s, characters: "done", scenes: "done", script: "done" }));
      showToast("success", `完成: ${sp.characters?.length || 0} 角色, ${sp.scenes?.length || 0} 场景`);
      setCurrentStep("script");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "未知错误";
      setError(msg);
      setStepStatus((s) => ({ ...s, characters: "error", scenes: "error", script: "error" }));
      showToast("error", `转换失败: ${msg}`);
    }
  };

  // ── 导出 YAML ──
  const handleExportYaml = async () => {
    setCurrentStep("export");
    setStepStatus((s) => ({ ...s, export: "loading" }));
    setError("");
    const payload = screenplay || { meta: {}, characters, scenes };
    try {
      const res = await fetch("/api/export/yaml", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ screenplay: payload, title: "" }),
      });
      if (!res.ok) throw new Error("导出失败");
      const data = await res.json();
      setYamlOutput(data.yaml || "");
      setStepStatus((s) => ({ ...s, export: "done" }));
      showToast("success", "YAML 生成完成");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "未知错误");
      setStepStatus((s) => ({ ...s, export: "error" }));
    }
  };

  const handleDownload = () => {
    const blob = new Blob([yamlOutput], { type: "text/yaml;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "screenplay.yml";
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(yamlOutput);
    showToast("success", "已复制到剪贴板");
  };

  // ── 渲染内容 ──
  const renderMain = () => {
    switch (currentStep) {
      case "input":
        return (
          <div>
            <h3>📖 章节预览</h3>
            <p style={{ fontSize: 13, color: "#666", marginBottom: 12 }}>
              共 {chapters.length.toLocaleString()} 字符。确认后开始转换。
            </p>
            <div className="chapter-list">
              {chapters.slice(0, 3000)}
              {chapters.length > 3000 && <p style={{ color: "#999" }}>...（仅显示前 3000 字符）</p>}
            </div>
            <button className="btn btn-primary" onClick={handleFullConvert} style={{ marginTop: 16 }}>
              🚀 一键全流程转换
            </button>
          </div>
        );

      case "characters":
        return (
          <div>
            <h3 style={{ marginBottom: 16 }}>👤 角色列表</h3>
            {error && <p style={{ color: "#c5221f", fontSize: 13, marginBottom: 12 }}>错误：{error}</p>}
            {characters.length === 0 && stepStatus.characters !== "loading" && (
              <div className="empty-state"><div className="icon">👤</div><p>点击"一键转换"开始</p></div>
            )}
            {stepStatus.characters === "loading" && <p>⏳ AI 正在分析角色...</p>}
            {characters.map((c) => (
              <div key={c.id} className="character-card">
                <div className="char-header">
                  <span className="char-name">{c.name}</span>
                  <span className="char-role">{c.role}</span>
                </div>
                <p style={{ fontSize: 13, color: "#666" }}>
                  {[c.gender, c.age, c.occupation].filter(Boolean).join(" · ")}
                </p>
                <p style={{ fontSize: 13, margin: "6px 0" }}>{c.description}</p>
                {c.traits.length > 0 && (
                  <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                    {c.traits.map((t) => (
                      <span key={t} style={{ fontSize: 12, padding: "2px 8px", background: "#f0f0f0", borderRadius: 10 }}>{t}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        );

      case "scenes":
        return (
          <div>
            <h3 style={{ marginBottom: 16 }}>🎬 场景列表</h3>
            {error && <p style={{ color: "#c5221f", fontSize: 13, marginBottom: 12 }}>错误：{error}</p>}
            {scenes.length === 0 && <div className="empty-state"><div className="icon">🎬</div><p>点击"一键转换"开始</p></div>}
            {scenes.map((s) => (
              <div key={s.id} className="scene-card">
                <div className="scene-header">
                  <div>
                    <span className="scene-number">第{s.scene_number}场 — {s.slug_line.location}</span>
                    <span style={{ marginLeft: 8, fontSize: 12, color: "#666" }}>
                      {TIME_LABELS[s.slug_line.time] || s.slug_line.time}
                    </span>
                  </div>
                </div>
                <div className="scene-body">
                  <p style={{ fontSize: 13, color: "#666", marginBottom: 8 }}>📍 {s.summary}</p>
                  {s.characters_present.length > 0 && (
                    <p style={{ fontSize: 12, marginBottom: 8 }}>出场：{s.characters_present.join(" · ")}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        );

      case "script":
        return (
          <div>
            <h3 style={{ marginBottom: 16 }}>📝 剧本预览</h3>
            {scenes.map((s) => (
              <div key={s.id} className="scene-card">
                <div className="scene-header">
                  <span className="scene-number">第{s.scene_number}场 — {s.slug_line.location}</span>
                </div>
                <div className="scene-body">
                  {s.content?.map((elem, j) => {
                    const cls = `content-element type-${elem.element_type}`;
                    if (elem.element_type === "action") return <div key={j} className={cls}>{elem.text}</div>;
                    if (elem.element_type === "dialogue") return (
                      <div key={j} className={cls}>
                        <span className="speaker">{elem.character_id || "?"}:</span>
                        {elem.parenthetical && <span style={{ fontStyle: "italic", color: "#666", fontSize: 12 }}>{elem.parenthetical} </span>}
                        {elem.text}
                      </div>
                    );
                    if (elem.element_type === "parenthetical") return <div key={j} className={cls}>{elem.text}</div>;
                    if (elem.element_type === "transition") return <div key={j} className={cls}>{elem.text}</div>;
                    return <div key={j} className={cls}><strong>[镜头]</strong> {elem.text}</div>;
                  })}
                </div>
              </div>
            ))}
          </div>
        );

      case "export":
        return (
          <div>
            <h3 style={{ marginBottom: 16 }}>📄 导出 YAML</h3>
            {error && <p style={{ color: "#c5221f", fontSize: 13, marginBottom: 12 }}>错误：{error}</p>}
            {!yamlOutput && stepStatus.export !== "done" && (
              <button className="btn btn-primary" onClick={handleExportYaml}>生成 YAML</button>
            )}
            {yamlOutput && (
              <>
                <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
                  <button className="btn btn-primary btn-sm" onClick={handleDownload}>📥 下载</button>
                  <button className="btn btn-secondary btn-sm" onClick={handleCopy}>📋 复制</button>
                  <button className="btn btn-secondary btn-sm" onClick={handleExportYaml}>🔄 重新生成</button>
                </div>
                <div className="yaml-preview">{yamlOutput}</div>
              </>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="workspace">
      <div className="workspace-sidebar">
        <div style={{ padding: "0 20px 16px", borderBottom: "1px solid #e0e0e0", marginBottom: 8 }}>
          <div style={{ fontWeight: 700, fontSize: 15 }}>🎬 创作工作台</div>
          <button onClick={() => navigate("/")} className="btn btn-sm" style={{ marginTop: 8, width: "100%", fontSize: 12 }}>
            ← 返回首页
          </button>
        </div>
        {STEPS.map((step) => {
          const status = stepStatus[step.key] || "idle";
          return (
            <div
              key={step.key}
              className={`step-item ${currentStep === step.key ? "active" : ""}`}
              onClick={() => { if (status === "done" || status === "idle") setCurrentStep(step.key); }}
            >
              <span className={`step-icon ${status}`}>
                {status === "loading" ? "⋯" : status === "done" ? "✓" : status === "error" ? "✗" : step.icon}
              </span>
              <span style={{ fontSize: 13 }}>{step.label}</span>
            </div>
          );
        })}
      </div>
      <div className="workspace-main">{renderMain()}</div>
      {toast && <div className={`toast ${toast.type}`}>{toast.msg}</div>}
    </div>
  );
}
