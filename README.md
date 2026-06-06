# 🎬 AI 剧本创作工具

将小说章节自动转换为结构化剧本（YAML 格式）的 AI 辅助创作工具。支持多章节小说文本输入，一键提取角色、拆分场景、生成标准剧本初稿。

## 功能概览

- 📥 **多格式输入**：支持粘贴纯文本、上传 .txt / .md / .docx / .pdf 文件
- 🤖 **AI 驱动转换**：三步 Pipeline — 角色提取 → 场景拆分 → 剧本生成
- 🔄 **一键/分步可选**：可一键全流程自动跑完，也可每步单独执行和重试
- 🎛️ **多模型切换**：工作台侧边栏实时切换 AI 模型（需在 .env 中预配置）
- 📄 **YAML 输出**：结构化剧本，可下载 / 复制
- 📊 **历史记录**：本地 SQLite 存储转换历史，可回看和删除
- 🔒 **隐私优先**：所有数据本地存储，API Key 由用户自行配置
- ⚡ **VS Code 一键启动**：`Ctrl+Shift+P` → 选"一键启动"，前后端同时跑

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | React 18 + TypeScript + Vite |
| 后端 | Python 3.12 + FastAPI |
| 数据库 | SQLite + SQLAlchemy (async) |
| AI | 兼容 OpenAI 接口规范（支持 OpenAI / DeepSeek / 通义千问 等） |

## 快速开始

### 1. 环境准备

- Python 3.10+
- Node.js 18+
- （可选）VS Code

### 2. 克隆项目

```bash
git clone git@github.com:zhangdidi876-dotcom/AI-Novel-to-Screenplay.git
cd AI-Novel-to-Screenplay
```

### 3. 配置 API Key

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，填入你的 AI 模型配置：

```env
# 必填
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=sk-你的真实Key
AI_MODEL_NAME=gpt-4o

# 可选：备选模型（前端可切换）
AI_MODELS_JSON=[{"name":"DeepSeek","base_url":"https://api.deepseek.com/v1","api_key":"sk-xxx","model_name":"deepseek-chat"}]
```

> 💡 **支持的服务商**（兼容 OpenAI Chat Completions 接口即可）：
> OpenAI / DeepSeek / 阿里通义千问 / 智谱 GLM / Moonshot / 等

### 4. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 5. 启动服务

**方式一：VS Code 一键启动（推荐）**

`Ctrl+Shift+P` → 输入 `Tasks: Run Task` → 选择 **🎬 一键启动 (前后端)**

**方式二：手动两个终端**

```bash
# 终端1 — 后端
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 终端2 — 前端
cd frontend
npm run dev
```

**方式三：Docker Compose**

```bash
docker-compose up -d
```

### 6. 打开浏览器

访问 `http://localhost:5173`

## 使用流程

1. **输入章节**：粘贴小说文本或上传文件（建议 ≥3 章）
2. **开始转换**：点击「🚀 一键全流程」或「分步开始」
3. **查看结果**：左侧导航切换查看角色 / 场景 / 剧本
4. **导出 YAML**：切换到「导出」标签，下载或复制
5. **查看历史**：侧边栏「📊 历史记录」随时回看

## API 端点

| 端点 | 用途 |
|------|------|
| `GET /api/health` | 健康检查 |
| `GET /api/models` | 可用模型列表 |
| `POST /api/upload` | 上传文件（.txt/.md/.docx/.pdf） |
| `POST /api/upload/text` | 粘贴文本 |
| `POST /api/extract/characters` | 角色提取 |
| `POST /api/extract/scenes` | 场景拆分 |
| `POST /api/generate/script` | 剧本生成 |
| `POST /api/convert/full` | 一键全流程 |
| `POST /api/export/yaml` | YAML 导出 |
| `POST /api/validate/yaml` | YAML 校验 |
| `GET /api/history` | 历史列表 |
| `GET /api/history/{id}` | 历史详情 |
| `DELETE /api/history/{id}` | 删除历史 |
| `POST /api/history/save` | 保存历史 |

## YAML 剧本格式

详见 [`docs/YAML_SCHEMA.md`](docs/YAML_SCHEMA.md) — 包含完整的 Schema 定义、设计原则和示例。

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理
│   │   ├── models/screenplay.py # 剧本数据模型
│   │   ├── routes/
│   │   │   ├── upload.py        # 文件上传与解析
│   │   │   ├── convert.py       # AI 转换流水线
│   │   │   └── history.py       # 历史记录
│   │   ├── services/
│   │   │   ├── ai_client.py     # AI 客户端
│   │   │   ├── character.py     # 角色提取 Prompt
│   │   │   ├── scene.py         # 场景拆分 Prompt
│   │   │   ├── script.py        # 剧本生成 Prompt
│   │   │   └── yaml_export.py   # YAML 序列化
│   │   └── db/                  # SQLite 数据库
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.tsx     # 输入页
│   │   │   ├── WorkspacePage.tsx # 工作台
│   │   │   └── HistoryPage.tsx  # 历史记录
│   │   ├── components/
│   │   │   └── ModelConfig.tsx  # 模型切换
│   │   ├── types/index.ts       # TS 类型定义
│   │   └── services/api.ts     # API 封装
│   └── package.json
├── .vscode/tasks.json           # VS Code 一键启动
├── docs/YAML_SCHEMA.md          # Schema 设计文档
└── docker-compose.yml
```

## 常见问题

**Q: 转换提示"AI 调用失败"？**
A: 检查 `backend/.env` 中 API Key 和 Base URL 是否正确。

**Q: 小说很长，AI 能处理吗？**
A: AI 的上下文窗口限制了单次处理量（通常 10-30 万字）。超长小说后续版本会加入自动分段处理。

**Q: 支持哪些 AI 模型？**
A: 所有兼容 OpenAI `/v1/chat/completions` 接口的服务，配置好 Base URL 即可。

## License

MIT
