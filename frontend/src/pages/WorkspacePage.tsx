import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import type { Character, Scene, Screenplay, StepStatus } from "../types";
import ModelConfig from "../components/ModelConfig";

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

  const loadSaved = <T,>(key: string, fallback: T): T => {
    try { const v = sessionStorage.getItem(key); return v ? JSON.parse(v) : fallback; }
    catch { return fallback; }
  };

  const [chapters, setChapters] = useState(() => sessionStorage.getItem("chapters_text") || "");
  const [showPreview, setShowPreview] = useState(false);
  const [modelIndex, setModelIndex] = useState(0);
  const [currentStep, setCurrentStep] = useState<StepKey>(
    () => loadSaved("ws_step", "input")
  );
  const [stepStatus, setStepStatus] = useState<Record<string, StepStatus>>(
    () => loadSaved("ws_status", { input: "done", characters: "idle", scenes: "idle", script: "idle", export: "idle" })
  );
  const [characters, setCharacters] = useState<Character[]>(() => loadSaved("ws_characters", []));
  const [scenes, setScenes] = useState<Scene[]>(() => loadSaved("ws_scenes", []));
  const [screenplay, setScreenplay] = useState<Screenplay | null>(() => loadSaved("ws_screenplay", null));
  const [yamlOutput, setYamlOutput] = useState(() => loadSaved("ws_yaml", ""));
  const [error, setError] = useState("");
  const [toast, setToast] = useState<{ type: "success" | "error"; msg: string } | null>(null);

  // 持久化到 sessionStorage
  useEffect(() => { if (currentStep) sessionStorage.setItem("ws_step", JSON.stringify(currentStep)); }, [currentStep]);
  useEffect(() => { sessionStorage.setItem("ws_status", JSON.stringify(stepStatus)); }, [stepStatus]);
  useEffect(() => { sessionStorage.setItem("ws_characters", JSON.stringify(characters)); }, [characters]);
  useEffect(() => { sessionStorage.setItem("ws_scenes", JSON.stringify(scenes)); }, [scenes]);
  useEffect(() => { sessionStorage.setItem("ws_screenplay", JSON.stringify(screenplay)); }, [screenplay]);
  useEffect(() => { if (yamlOutput) sessionStorage.setItem("ws_yaml", JSON.stringify(yamlOutput)); }, [yamlOutput]);

  useEffect(() => {
    if (!chapters) {
      const text = sessionStorage.getItem("chapters_text");
      if (!text) { navigate("/"); return; }
      setChapters(text);
    }
  }, [navigate, chapters]);

  const anyLoading = Object.values(stepStatus).some((s) => s === "loading");

  const showToast = useCallback((type: "success" | "error", msg: string) => {
    setToast({ type, msg });
    setTimeout(() => setToast(null), 3500);
  }, []);

  const apiCall = async (url: string): Promise<any> => {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: chapters, model_index: modelIndex }),
    });
    if (!res.ok) { const e = await res.json(); throw new Error(e.detail || "请求失败"); }
    return res.json();
  };

  // ── 分步：角色提取 ──
  const handleExtractCharacters = async () => {
    setCurrentStep("characters");
    setStepStatus((s) => ({ ...s, characters: "loading" }));
    setError("");
    try {
      const data = await apiCall("/api/extract/characters");
      setCharacters(data.characters || []);
      setStepStatus((s) => ({ ...s, characters: "done" }));
      showToast("success", `提取 ${data.count || 0} 个角色`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "未知错误");
      setStepStatus((s) => ({ ...s, characters: "error" }));
      showToast("error", "角色提取失败");
    }
  };

  // ── 分步：场景拆分（无角色时自动先提取） ──
  const handleExtractScenes = async () => {
    setCurrentStep("scenes");
    if (characters.length === 0) {
      setStepStatus((s) => ({ ...s, characters: "loading", scenes: "loading" }));
      showToast("success", "先自动提取角色...");
      try {
        const charData = await apiCall("/api/extract/characters");
        setCharacters(charData.characters || []);
        setStepStatus((s) => ({ ...s, characters: "done" }));
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "未知错误");
        setStepStatus((s) => ({ ...s, characters: "error", scenes: "error" }));
        showToast("error", "角色提取失败");
        return;
      }
    } else {
      setStepStatus((s) => ({ ...s, scenes: "loading" }));
    }
    setError("");
    try {
      const data = await apiCall("/api/extract/scenes");
      if (data.characters) setCharacters(data.characters);
      setScenes(data.scenes || []);
      setStepStatus((s) => ({ ...s, characters: "done", scenes: "done" }));
      showToast("success", `拆分 ${data.scene_count || 0} 个场景`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "未知错误");
      setStepStatus((s) => ({ ...s, scenes: "error" }));
      showToast("error", "场景拆分失败");
    }
  };

  // ── 分步：剧本生成（无角色/场景时自动先执行） ──
  const handleGenerateScript = async () => {
    setCurrentStep("script");
    setStepStatus((s) => ({ ...s, script: "loading" }));
    setError("");
    try {
      // 无角色时自动提取
      if (characters.length === 0) {
        setStepStatus((s) => ({ ...s, characters: "loading" }));
        const charData = await apiCall("/api/extract/characters");
        setCharacters(charData.characters || []);
        setStepStatus((s) => ({ ...s, characters: "done" }));
      }
      // 无场景时自动拆分
      if (scenes.length === 0) {
        setCurrentStep("scenes");
        setStepStatus((s) => ({ ...s, scenes: "loading" }));
        const sceneData = await apiCall("/api/extract/scenes");
        if (sceneData.characters) setCharacters(sceneData.characters);
        setScenes(sceneData.scenes || []);
        setStepStatus((s) => ({ ...s, scenes: "done" }));
      }
      const data = await apiCall("/api/generate/script");
      const sp = data.screenplay as Screenplay;
      setScreenplay(sp);
      if (sp.characters) setCharacters(sp.characters);
      if (sp.scenes) setScenes(sp.scenes);
      setStepStatus((s) => ({ ...s, characters: "done", scenes: "done", script: "done" }));
      showToast("success", "剧本生成完成");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "未知错误");
      setStepStatus((s) => ({ ...s, script: "error" }));
      showToast("error", "剧本生成失败");
    }
  };

  const doSaveHistory = async (yaml: string) => {
    try {
      const chMatch = chapters.match(/(第\s*[一二三四五六七八九十百千0-9]+\s*章|Chapter\s+\d+)/gi);
      await fetch("/api/history/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: screenplay?.meta?.title || "未命名项目",
          chapter_count: chMatch ? chMatch.length : 0,
          model_name: `model_${modelIndex}`,
          input_text: chapters,
          output_yaml: yaml,
        }),
      });
    } catch { /* 静默失败，不影响主流程 */ }
  };

  // ── 一键全流程 ──
  const handleFullConvert = async () => {
    setCurrentStep("characters");
    setStepStatus((s) => ({ ...s, characters: "loading", scenes: "idle", script: "idle", export: "idle" }));
    setError("");
    try {
      const res = await fetch("/api/convert/full", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: chapters, model_index: modelIndex }),
      });
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || "请求失败"); }
      const data = await res.json();
      const sp = data.screenplay as Screenplay;
      setScreenplay(sp);
      if (sp.characters) setCharacters(sp.characters);
      if (sp.scenes) setScenes(sp.scenes);
      setStepStatus((s) => ({ ...s, characters: "done", scenes: "done", script: "done" }));
      showToast("success", `完成: ${sp.characters?.length || 0} 角色, ${sp.scenes?.length || 0} 场景`);
      doSaveHistory("");
      setCurrentStep("script");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "未知错误";
      setError(msg);
      setStepStatus((s) => ({ ...s, characters: "error", scenes: "error", script: "error" }));
      showToast("error", `转换失败: ${msg}`);
    }
  };

  // ── 导出 YAML（自动保存历史）──
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
      const yaml = data.yaml || "";
      setYamlOutput(yaml);
      await doSaveHistory(yaml);
      setStepStatus((s) => ({ ...s, export: "done" }));
      showToast("success", "YAML 已生成，历史已自动保存");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "未知错误");
      setStepStatus((s) => ({ ...s, export: "error" }));
    }
  };

  const handleDownload = () => {
    const blob = new Blob([yamlOutput], { type: "text/yaml;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "screenplay.yaml";
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
              <button
                onClick={() => setShowPreview(!showPreview)}
                style={{
                  marginLeft: 10, padding: "2px 10px", fontSize: 12,
                  background: "#f0f0f0", border: "1px solid #ddd", borderRadius: 4, cursor: "pointer",
                }}
              >
                {showPreview ? "收起 ▲" : "展开查看 ▼"}
              </button>
            </p>
            {showPreview && <div className="chapter-list">{chapters}</div>}
            <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
              <button className="btn btn-primary" onClick={handleFullConvert}>🚀 一键全流程</button>
              <button className="btn btn-secondary" onClick={handleExtractCharacters}>分步：角色提取 →</button>
            </div>
          </div>
        );

      case "characters":
        return (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h3>👤 角色列表</h3>
              <div style={{ display: "flex", gap: 8 }}>
                {characters.length > 0 && (
                  <>
                    <button className="btn btn-secondary btn-sm" onClick={handleExtractCharacters}>🔄 重新提取</button>
                    <button className="btn btn-primary btn-sm" onClick={handleExtractScenes}>下一步：场景拆分 →</button>
                  </>
                )}
              </div>
            </div>
            {error && <p style={{ color: "#c5221f", fontSize: 13, marginBottom: 12 }}>错误：{error}</p>}
            {characters.length === 0 && stepStatus.characters !== "loading" && (
              <div className="empty-state"><div className="icon">👤</div><p>点击"一键转换"或"分步"开始</p></div>
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
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h3>🎬 场景列表</h3>
              <div style={{ display: "flex", gap: 8 }}>
                {scenes.length > 0 && (
                  <>
                    <button className="btn btn-secondary btn-sm" onClick={handleExtractScenes}>🔄 重新拆分</button>
                    <button className="btn btn-primary btn-sm" onClick={handleGenerateScript}>下一步：生成剧本 →</button>
                  </>
                )}
              </div>
            </div>
            {error && <p style={{ color: "#c5221f", fontSize: 13, marginBottom: 12 }}>错误：{error}</p>}
            {scenes.length === 0 && <div className="empty-state"><div className="icon">🎬</div><p>先提取角色后再拆分场景</p></div>}
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
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h3>📝 剧本预览</h3>
              <div style={{ display: "flex", gap: 8 }}>
                {scenes.length > 0 && (
                  <>
                    <button className="btn btn-secondary btn-sm" onClick={handleGenerateScript}>🔄 重新生成</button>
                    <button className="btn btn-primary btn-sm" onClick={handleExportYaml}>导出 YAML →</button>
                  </>
                )}
              </div>
            </div>
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
    <>
      <nav className="navbar">
        <span className="navbar-brand" onClick={() => navigate("/")}>🎬 AI 剧本创作工具</span>
        <div className="navbar-links">
          <button onClick={() => navigate("/")}>🏠 首页</button>
          <button onClick={() => navigate("/history")}>📊 历史</button>
        </div>
      </nav>
      <div className="workspace">
        <div className="workspace-sidebar">
          <div style={{ padding: "12px 20px 12px", borderBottom: "1px solid #e0e0e0", marginBottom: 4 }}>
            <div style={{ fontWeight: 700, fontSize: 14, color: "#1a73e8", marginBottom: 10 }}>转换步骤</div>
            <ModelConfig modelIndex={modelIndex} onModelChange={setModelIndex} />
          </div>
          {STEPS.map((step) => {
            const status = stepStatus[step.key] || "idle";
          return (
            <div
              key={step.key}
              className={`step-item ${currentStep === step.key ? "active" : ""}`}
              onClick={() => {
                // 加载中任何步骤都可以切换视角查看
                if (status === "loading" || status === "done" || status === "idle" || status === "error") {
                  setCurrentStep(step.key);
                }
                // 仅在无加载任务时，点击未执行步骤才自动触发
                if (!anyLoading && status === "idle") {
                  if (step.key === "characters") handleExtractCharacters();
                  else if (step.key === "scenes") handleExtractScenes();
                  else if (step.key === "script") handleGenerateScript();
                }
              }}
            >
              <span className={`step-icon ${status}`}>
                {status === "loading" ? "⋯" : status === "done" ? "✓" : status === "error" ? "✗" : step.icon}
              </span>
              <span style={{ fontSize: 13 }}>{step.label}</span>
            </div>
          );
        })}
      </div>
      <div className="workspace-main">
        {anyLoading && (
          <div style={{
            background: "#e8f0fe", border: "1px solid #a8c8fa", borderRadius: 6,
            padding: "10px 16px", marginBottom: 16, fontSize: 13, color: "#1a73e8",
            display: "flex", alignItems: "center", gap: 8,
          }}>
            <span style={{ animation: "pulse 1s infinite", fontSize: 16 }}>⏳</span>
            {stepStatus.characters === "loading" && "正在提取角色..."}
            {stepStatus.scenes === "loading" && "正在拆分场景..."}
            {stepStatus.script === "loading" && "正在生成剧本..."}
            {stepStatus.export === "loading" && "正在导出 YAML..."}
            <span style={{ fontSize: 11, color: "#666" }}>（可自由切换左侧步骤查看历史结果）</span>
          </div>
        )}
        {renderMain()}
      </div>
      {toast && <div className={`toast ${toast.type}`}>{toast.msg}</div>}
    </div>
    </>
  );
}
