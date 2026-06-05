import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function HomePage() {
  const navigate = useNavigate();
  const [text, setText] = useState("");
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("/api/upload", { method: "POST", body: form });
      const data = await res.json();
      setText(data.text || "");
    } catch (err) {
      alert("文件上传失败");
    }
    setUploading(false);
  };

  const handleStart = () => {
    if (!text.trim()) return;
    sessionStorage.setItem("chapters_text", text);
    navigate("/workspace");
  };

  return (
    <div style={{ maxWidth: 720, margin: "60px auto", padding: 24, fontFamily: "system-ui" }}>
      <h1>🎬 AI 剧本创作工具</h1>
      <p style={{ color: "#666" }}>
        将小说章节转换为结构化剧本 YAML，支持 ≥3 章以上文本。粘贴章节内容或上传文件即可开始。
      </p>

      <div style={{ marginTop: 24 }}>
        <label style={{ display: "block", marginBottom: 8, fontWeight: 600 }}>
          上传章节文件（.txt / .docx / .pdf）
        </label>
        <input
          type="file"
          accept=".txt,.docx,.pdf"
          onChange={handleFileUpload}
          disabled={uploading}
        />
        {uploading && <span style={{ marginLeft: 8 }}>解析中...</span>}
      </div>

      <div style={{ marginTop: 24 }}>
        <label style={{ display: "block", marginBottom: 8, fontWeight: 600 }}>
          或直接粘贴章节文本（用 "第X章" 或 "Chapter X" 分隔）
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={`第1章 标题…\n（正文内容）\n\n第2章 标题…\n（正文内容）\n\n第3章 标题…\n（正文内容）`}
          rows={16}
          style={{ width: "100%", padding: 12, fontSize: 14, border: "1px solid #ccc", borderRadius: 6 }}
        />
      </div>

      <button
        onClick={handleStart}
        disabled={!text.trim()}
        style={{
          marginTop: 20,
          padding: "12px 32px",
          fontSize: 16,
          background: text.trim() ? "#1a73e8" : "#ccc",
          color: "#fff",
          border: "none",
          borderRadius: 6,
          cursor: text.trim() ? "pointer" : "default",
        }}
      >
        开始转换
      </button>
    </div>
  );
}
