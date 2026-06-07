import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function HomePage() {
  const navigate = useNavigate();
  const [text, setText] = useState("");
  const [uploading, setUploading] = useState(false);
  const [chapterCount, setChapterCount] = useState(0);
  const [healthOk, setHealthOk] = useState<boolean | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((d) => setHealthOk(d.status === "ok"))
      .catch(() => setHealthOk(false));
  }, []);

  useEffect(() => {
    const matches = text.match(/(第\s*[一二三四五六七八九十百千0-9]+\s*章|Chapter\s+\d+)/gi);
    setChapterCount(matches ? matches.length : 0);
  }, [text]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("/api/upload", { method: "POST", body: form });
      const data = await res.json();
      if (data.error) { alert(data.error); }
      else { setText(data.text || ""); }
    } catch {
      alert("文件上传失败，请确认后端已启动");
    }
    setUploading(false);
  };

  const [detecting, setDetecting] = useState(false);

  const handleSmartDetect = async () => {
    if (!text.trim()) return;
    setDetecting(true);
    try {
      const res = await fetch("/api/detect/chapters", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (data.chapter_count >= 2) {
        const formatted = data.chapters.map((c: any) =>
          `第${c.number}章 ${c.title}\n${c.content}`).join("\n\n");
        setText(formatted);
        alert(`✅ 检测到 ${data.chapter_count} 个章节，已自动格式化`);
      } else {
        const aiRes = await fetch("/api/detect/chapters/ai", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
        const aiData = await aiRes.json();
        if (aiData.chapter_count >= 2) {
          const formatted = aiData.chapters.map((c: any) =>
            `第${c.number}章 ${c.title}\n${c.content}`).join("\n\n");
          setText(formatted);
          alert(`🤖 AI 检测到 ${aiData.chapter_count} 个章节，已自动格式化`);
        } else {
          alert("未检测到章节结构，将作为全文处理。如有多章，请确保章节间有明显分界。");
        }
      }
    } catch { alert("检测失败，请检查后端"); }
    setDetecting(false);
  };

  const handleStart = () => {
    if (!text.trim()) return;
    const id = Date.now().toString(36);
    sessionStorage.setItem(`conv_${id}_text`, text);
    // 添加到活跃列表
    const list = (() => {
      try { return JSON.parse(sessionStorage.getItem("conv_list") || "[]"); }
      catch { return []; }
    })();
    list.unshift(id);
    if (list.length > 10) list.length = 10; // 最多保留10个
    sessionStorage.setItem("conv_list", JSON.stringify(list));
    navigate(`/workspace?id=${id}`);
  };

  return (
    <>
      <nav className="navbar">
        <span className="navbar-brand" onClick={() => navigate("/")}>🎬 AI 剧本创作工具</span>
        <div className="navbar-links">
          <span className={`navbar-status ${healthOk ? "ok" : healthOk === false ? "err" : ""}`}>
            {healthOk === null ? "检测中..." : healthOk ? "✅ 已连接" : "❌ 未连接"}
          </span>
          <button onClick={() => navigate("/history")}>📊 历史记录</button>
        </div>
      </nav>
      <div style={{ maxWidth: 720, margin: "60px auto", padding: 24 }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <h1 className="hero-title">将小说<mark>转化为</mark>剧本</h1>
          <p className="hero-subtitle">
            AI 自动提取角色、拆分场景、生成结构化剧本（YAML 格式）
          </p>
        </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-title">📂 上传章节文件</div>
        <p style={{ fontSize: 12, color: "var(--text-dim)", marginBottom: 8 }}>
          支持 .txt / .md / .docx / .pdf 格式
        </p>
        <input
          type="file" accept=".txt,.md,.docx,.pdf"
          onChange={handleFileUpload} disabled={uploading}
          style={{ fontSize: 14 }}
        />
        {uploading && <span style={{ marginLeft: 8, fontSize: 13 }}>解析中...</span>}
      </div>

      <div className="card">
        <div className="card-title">
          📝 粘贴章节文本
          {text.trim() && (
            <button
              onClick={handleSmartDetect} disabled={detecting}
              className="btn btn-sm"
              style={{ marginLeft: 12, fontSize: 12, background: "#e8f0fe", color: "#1a73e8" }}
            >
              {detecting ? "⏳ 识别中..." : "🔍 智能分段"}
            </button>
          )}
        </div>
        <p style={{ fontSize: 12, color: "var(--text-dim)", marginBottom: 8 }}>
          支持任意格式粘贴，点击「智能分段」自动识别章节边界
        </p>
        <textarea
          value={text} onChange={(e) => setText(e.target.value)}
          placeholder={`第1章 标题…\n（正文内容）\n\n第2章 标题…\n（正文内容）\n\n第3章 标题…\n（正文内容）`}
          rows={16} className="form-input"
        />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 8 }}>
          <span style={{ fontSize: 12, color: "var(--text-dim)" }}>已输入 {text.length.toLocaleString()} 个字符</span>
          {text && (
            <button onClick={() => setText("")}
              style={{ padding: "4px 12px", fontSize: 12, color: "var(--text-secondary)", background: "rgba(255,255,255,0.06)", border: "1px solid var(--border)", borderRadius: 4, cursor: "pointer" }}>
              清空文本
            </button>
          )}
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16 }}>
          <div>
            <span className={`chapter-badge ${chapterCount >= 3 ? "good" : chapterCount > 0 ? "warn" : "none"}`}>
              📊 检测到 {chapterCount} 章
            </span>
            {text.trim() && chapterCount < 3 && (
              <span style={{ fontSize: 12, color: "var(--accent-orange)", marginLeft: 8 }}>
                章节较少，剧本可能不完整
              </span>
            )}
          </div>
          <button onClick={handleStart} disabled={!text.trim()}
            className={`btn ${text.trim() ? "btn-primary" : ""}`}
            style={!text.trim() ? { background: "var(--text-dim)", color: "#fff" } : {}}>
            开始转换 →
          </button>
        </div>
      </div>
      </div>
    </>
  );
}
