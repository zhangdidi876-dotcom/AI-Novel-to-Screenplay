import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

interface HistoryItem {
  id: number;
  title: string;
  chapter_count: number;
  model_name: string;
  created_at: string;
}

export default function HistoryPage() {
  const navigate = useNavigate();
  const [list, setList] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [detailId, setDetailId] = useState<number | null>(null);
  const [detail, setDetail] = useState<{ input_text: string; output_yaml: string } | null>(null);

  useEffect(() => {
    fetch("/api/history")
      .then((r) => r.json())
      .then((d) => { setList(d.history || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const handleView = async (id: number) => {
    setDetailId(id);
    try {
      const res = await fetch(`/api/history/${id}`);
      const d = await res.json();
      setDetail(d);
    } catch {
      setDetail(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("确定删除？")) return;
    await fetch(`/api/history/${id}`, { method: "DELETE" });
    setList((l) => l.filter((r) => r.id !== id));
    if (detailId === id) { setDetailId(null); setDetail(null); }
  };

  return (
    <div style={{ maxWidth: 860, margin: "40px auto", padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h2>📊 转换历史</h2>
        <button onClick={() => navigate("/")} className="btn btn-secondary btn-sm">← 返回首页</button>
      </div>

      {loading && <p style={{ color: "#999" }}>加载中...</p>}

      {!loading && list.length === 0 && (
        <div className="empty-state">
          <div className="icon">📭</div>
          <p>暂无历史记录</p>
          <button onClick={() => navigate("/")} className="btn btn-primary btn-sm" style={{ marginTop: 12 }}>
            去创建新转换
          </button>
        </div>
      )}

      {list.map((r) => (
        <div key={r.id} className="card" style={{ marginBottom: 10 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontWeight: 600 }}>{r.title || "未命名项目"}</div>
              <div style={{ fontSize: 12, color: "#999" }}>
                {r.chapter_count} 章 · 模型 {r.model_name} · {r.created_at?.slice(0, 10)}
              </div>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-sm" onClick={() => handleView(r.id)}>
                {detailId === r.id ? "收起" : "查看"}
              </button>
              <button className="btn btn-sm" style={{ color: "#c5221f" }} onClick={() => handleDelete(r.id)}>
                删除
              </button>
            </div>
          </div>
          {detailId === r.id && detail && (
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 12, color: "#999", marginBottom: 8 }}>
                原文 {detail.input_text?.length?.toLocaleString() || 0} 字符
              </div>
              <div className="yaml-preview" style={{ maxHeight: 300 }}>
                {detail.output_yaml?.slice(0, 2000)}
                {(detail.output_yaml?.length || 0) > 2000 && "\n...（已截断）"}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
