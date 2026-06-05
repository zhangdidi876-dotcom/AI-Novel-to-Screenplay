import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function WorkspacePage() {
  const navigate = useNavigate();
  const [chapters, setChapters] = useState("");

  useEffect(() => {
    const text = sessionStorage.getItem("chapters_text");
    if (!text) {
      navigate("/");
      return;
    }
    setChapters(text);
  }, [navigate]);

  return (
    <div style={{ maxWidth: 960, margin: "40px auto", padding: 24, fontFamily: "system-ui" }}>
      <h2>📝 转换工作台</h2>
      <p style={{ color: "#666" }}>已加载 {chapters.length} 字符。功能将在后续版本逐步完善。</p>
      <button onClick={() => navigate("/")} style={{ marginTop: 12 }}>
        ← 返回首页
      </button>
    </div>
  );
}
