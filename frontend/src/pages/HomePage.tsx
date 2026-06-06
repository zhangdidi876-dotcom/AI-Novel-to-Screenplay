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

  const handleStart = () => {
    if (!text.trim()) return;
    sessionStorage.setItem("chapters_text", text);
    navigate("/workspace");
  };

  return (
    <div style={{ maxWidth: 720, margin: "40px auto", padding: 24 }}>
      <div style={{ textAlign: "center", marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, marginBottom: 8 }}>🎬 AI 剧本创作工具</h1>
        <p style={{ color: "#666", fontSize: 14 }}>
          将小说文本自动转换为结构化剧本（YAML 格式）
        </p>
        <p style={{ fontSize: 12, color: "#999", marginTop: 4 }}>
          后端：
          <span style={{ color: healthOk ? "#1e8e3e" : healthOk === false ? "#c5221f" : "#999" }}>
            {healthOk === null ? "检测中..." : healthOk ? "✅ 已连接" : "❌ 未连接"}
          </span>
          <span style={{ margin: "0 12px" }}>|</span>
          <a href="/history" onClick={(e) => { e.preventDefault(); navigate("/history"); }}
             style={{ color: "#1a73e8", textDecoration: "none" }}>
            📊 历史记录
          </a>
        </p>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-title">📂 上传章节文件</div>
        <p style={{ fontSize: 12, color: "#999", marginBottom: 8 }}>
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
        <div className="card-title">📝 或直接粘贴章节文本</div>
        <p style={{ fontSize: 12, color: "#999", marginBottom: 8 }}>
          用 "第X章" 或 "Chapter X" 分隔章节（建议 3 章以上）
        </p>
        <textarea
          value={text} onChange={(e) => setText(e.target.value)}
          placeholder={`第1章 标题…\n（正文内容）\n\n第2章 标题…\n（正文内容）\n\n第3章 标题…\n（正文内容）`}
          rows={16} className="form-input"
        />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 8 }}>
          <span style={{ fontSize: 12, color: "#999" }}>已输入 {text.length.toLocaleString()} 个字符</span>
          {text && (
            <button onClick={() => setText("")}
              style={{ padding: "4px 12px", fontSize: 12, color: "#666", background: "#f0f0f0", border: "1px solid #ddd", borderRadius: 4, cursor: "pointer" }}>
              清空文本
            </button>
          )}
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16 }}>
          <div>
            <span style={{ fontSize: 13, color: chapterCount >= 3 ? "#1e8e3e" : chapterCount > 0 ? "#e37400" : "#999" }}>
              📊 检测到 {chapterCount} 章
            </span>
            {text.trim() && chapterCount < 3 && (
              <span style={{ fontSize: 12, color: "#e37400", marginLeft: 8 }}>
                （章节较少，剧本可能不完整）
              </span>
            )}
          </div>
          <button onClick={handleStart} disabled={!text.trim()}
            className={`btn ${text.trim() ? "btn-primary" : ""}`}
            style={!text.trim() ? { background: "#ccc", color: "#fff" } : {}}>
            开始转换 →
          </button>
        </div>
      </div>
    </div>
  );
}
