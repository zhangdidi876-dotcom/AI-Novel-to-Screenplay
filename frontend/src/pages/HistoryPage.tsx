import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

interface HistoryItem {
  id: number;
  session_id: string;
  title: string;
  chapter_count: number;
  model_name: string;
  status: string;
  created_at: string;
}

const STATUS_MAP: Record<string, { label: string; color: string; bg: string }> = {
  running: { label: "进行中", color: "#e37400", bg: "#fef7e0" },
  partial: { label: "部分完成", color: "#1a73e8", bg: "#e8f0fe" },
  completed: { label: "已完成", color: "#1e8e3e", bg: "#e6f4ea" },
};

export default function HistoryPage() {
  const navigate = useNavigate();
  const [list, setList] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [renamingId, setRenamingId] = useState<number | null>(null);
  const [renameText, setRenameText] = useState("");

  const refresh = () => {
    fetch("/api/history")
      .then((r) => r.json())
      .then((d) => { setList(d.history || []); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { refresh(); }, []);

  const handleDelete = async (id: number) => {
    if (!confirm("确定删除？")) return;
    await fetch(`/api/history/${id}`, { method: "DELETE" });
    setList((l) => l.filter((r) => r.id !== id));
  };

  const startRename = (r: HistoryItem) => {
    setRenamingId(r.id);
    setRenameText(r.title);
  };

  const confirmRename = async (id: number) => {
    if (!renameText.trim()) return;
    await fetch(`/api/history/${id}/rename`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: renameText }),
    });
    setList((l) => l.map((r) => (r.id === id ? { ...r, title: renameText } : r)));
    setRenamingId(null);
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
            <div style={{ flex: 1 }}>
              {renamingId === r.id ? (
                <div style={{ display: "flex", gap: 8 }}>
                  <input
                    value={renameText}
                    onChange={(e) => setRenameText(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") confirmRename(r.id); if (e.key === "Escape") setRenamingId(null); }}
                    className="form-input"
                    style={{ width: 200, padding: "4px 8px" }}
                    autoFocus
                  />
                  <button className="btn btn-sm btn-primary" onClick={() => confirmRename(r.id)}>确定</button>
                  <button className="btn btn-sm" onClick={() => setRenamingId(null)}>取消</button>
                </div>
              ) : (
                <div style={{ fontWeight: 600, cursor: "pointer" }} onClick={() => navigate(`/history/${r.id}`)}>
                  {r.title || "未命名项目"}
                  <span style={{ fontSize: 11, color: "#999", marginLeft: 8, fontWeight: 400 }}>点击查看详情 →</span>
                </div>
              )}
              <div style={{ fontSize: 12, color: "#999" }}>
                {r.chapter_count} 章 · {r.created_at?.slice(0, 10)}
                <span style={{
                  fontSize: 11, marginLeft: 6, padding: "1px 6px", borderRadius: 8,
                  background: (STATUS_MAP[r.status] || STATUS_MAP.completed).bg,
                  color: (STATUS_MAP[r.status] || STATUS_MAP.completed).color,
                }}>
                  {(STATUS_MAP[r.status] || STATUS_MAP.completed).label}
                </span>
              </div>
            </div>
            <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
              {r.session_id && r.status !== "completed" && (
                <button className="btn btn-sm btn-primary"
                  onClick={() => navigate(`/workspace?id=${r.session_id}`)}>继续</button>
              )}
              <button className="btn btn-sm" onClick={() => navigate(`/history/${r.id}`)}>查看</button>
              <button className="btn btn-sm" onClick={() => startRename(r)}>✏️</button>
              <button className="btn btn-sm" style={{ color: "#c5221f" }} onClick={() => handleDelete(r.id)}>删除</button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
