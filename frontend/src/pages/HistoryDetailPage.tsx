import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import yaml from "js-yaml";
import type { Screenplay } from "../types";

function downloadYaml(content: string) {
  const blob = new Blob([content], { type: "text/yaml;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "screenplay.yaml";
  a.click();
  URL.revokeObjectURL(a.href);
}

export default function HistoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [record, setRecord] = useState<any>(null);
  const [screenplay, setScreenplay] = useState<Screenplay | null>(null);
  const [tab, setTab] = useState<"characters" | "scenes" | "script" | "yaml">("characters");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/history/${id}`)
      .then((r) => r.json())
      .then((d) => {
        setRecord(d);
        if (d.output_yaml) {
          try {
            const parsed: any = yaml.load(d.output_yaml);
            setScreenplay(parsed?.screenplay || parsed || null);
          } catch {}
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  const charName = (characterId: string) =>
    screenplay?.characters?.find((c: any) => c.id === characterId)?.name || characterId;

  if (loading) return <div style={{ padding: 40, textAlign: "center", color: "#999" }}>加载中...</div>;
  if (!record) return <div style={{ padding: 40, textAlign: "center", color: "#c5221f" }}>记录不存在</div>;

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <nav className="navbar" style={{ margin: "-24px -24px 24px", padding: "0 24px" }}>
        <span className="navbar-brand" onClick={() => navigate("/")}>🎬 AI 剧本创作工具</span>
        <div className="navbar-links">
          <button onClick={() => navigate("/history")}>📊 返回历史</button>
        </div>
      </nav>

      <h2>{record.title || "未命名项目"}</h2>
      <p style={{ fontSize: 13, color: "#999", marginBottom: 16 }}>
        {record.chapter_count} 章 · {record.created_at?.slice(0, 10)} · 状态: {record.status}
      </p>

      {!screenplay ? (
        <div className="empty-state">
          <div className="icon">📭</div>
          <p>该转换尚未生成剧本内容</p>
          {record.session_id && (
            <button className="btn btn-primary btn-sm" style={{ marginTop: 12 }}
              onClick={() => navigate(`/workspace?id=${record.session_id}`)}>
              继续转换
            </button>
          )}
        </div>
      ) : (
        <>
          <div className="tabs">
            {(["characters", "scenes", "script", "yaml"] as const).map((t) => (
              <button key={t} className={`tab ${tab === t ? "active" : ""}`} onClick={() => setTab(t)}>
                {{ characters: "👤 角色", scenes: "🎬 场景", script: "📝 剧本", yaml: "📄 YAML" }[t]}
              </button>
            ))}
          </div>

          {tab === "characters" && (
            <div>
              {(screenplay.characters || []).map((c: any) => (
                <div key={c.id} className="character-card">
                  <div className="char-header">
                    <span className="char-name">{c.name}</span>
                    <span className="char-role">{c.role}</span>
                  </div>
                  <p style={{ fontSize: 13, color: "#666" }}>
                    {[c.gender, c.age, c.occupation].filter(Boolean).join(" · ")}
                  </p>
                  <p style={{ fontSize: 13, margin: "6px 0" }}>{c.description}</p>
                  {c.traits?.length > 0 && (
                    <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                      {c.traits.map((t: string) => (
                        <span key={t} style={{ fontSize: 12, padding: "2px 8px", background: "#f0f0f0", borderRadius: 10 }}>{t}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {tab === "scenes" && (
            <div>
              {(screenplay.scenes || []).map((s: any) => (
                <div key={s.id} className="scene-card">
                  <div className="scene-header">
                    <span className="scene-number">第{s.scene_number}场 — {s.slug_line}</span>
                  </div>
                  <div className="scene-body">
                    <p style={{ fontSize: 13, color: "#666" }}>📍 {s.summary}</p>
                    {s.characters_present?.length > 0 && (
                      <p style={{ fontSize: 12, marginTop: 6 }}>出场：{s.characters_present.map(charName).join(" · ")}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {tab === "script" && (
            <div>
              {(screenplay.scenes || []).map((s: any) => (
                <div key={s.id} className="scene-card">
                  <div className="scene-header">
                    <span className="scene-number">第{s.scene_number}场 — {s.slug_line}</span>
                  </div>
                  <div className="scene-body">
                    {(s.content || []).map((elem: any, j: number) => {
                      const cls = `content-element type-${elem.element_type}`;
                      if (elem.element_type === "action") return <div key={j} className={cls}>{elem.text}</div>;
                      if (elem.element_type === "dialogue") return (
                        <div key={j} className={cls}>
                          <span className="speaker">{charName(elem.character_id)}:</span>
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
          )}

          {tab === "yaml" && (
            <div>
              <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
                <button className="btn btn-primary btn-sm" onClick={() => downloadYaml(record.output_yaml)}>📥 下载</button>
                <button className="btn btn-secondary btn-sm" onClick={() => { navigator.clipboard.writeText(record.output_yaml); alert("已复制"); }}>📋 复制</button>
              </div>
              <div className="yaml-preview">{record.output_yaml}</div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
