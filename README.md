# 🎬 AI 剧本创作工具

将小说章节自动转换为结构化剧本（YAML 格式）的 AI 辅助创作工具。支持 3 章以上小说文本输入，一键提取角色、拆分场景、生成标准剧本初稿。

## 功能概览

- 📥 **多格式输入**：支持粘贴纯文本、上传 .txt / .docx / .pdf 文件
- 🤖 **AI 驱动转换**：自动提取角色、拆分场景、生成对白与动作描写
- 🔧 **分步可编辑**：每步 AI 结果可人工审核和修改后继续
- 📄 **YAML 输出**：结构化剧本，可下载、可版本管理、可进一步打磨
- 📊 **历史记录**：本地 SQLite 存储转换历史，随时回溯
- 🔒 **隐私优先**：所有数据本地存储，API Key 由用户自行配置

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | React 18 + TypeScript + Vite |
| 后端 | Python 3.12 + FastAPI |
| 数据库 | SQLite + SQLAlchemy (async) |
| AI | 兼容 OpenAI 接口规范（支持 OpenAI / Claude / DeepSeek / 通义千问 等） |
| 部署 | Docker Compose |

## 快速开始

### 1. 环境准备

- Python 3.12+
- Node.js 20+
- （可选）Docker & Docker Compose

### 2. 克隆仓库

```bash
git clone <repo-url>
cd screenplay-tool
```

### 3. 配置 API Key

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，填入你的 AI 模型配置：

```env
# 必填：至少配置一个模型
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=sk-your-api-key-here
AI_MODEL_NAME=gpt-4o

# 可选：备选模型（多个模型可在前端切换）
AI_MODELS_JSON=[{"name":"GPT-4o","base_url":"https://api.openai.com/v1","api_key":"sk-...","model_name":"gpt-4o"},{"name":"DeepSeek","base_url":"https://api.deepseek.com/v1","api_key":"sk-...","model_name":"deepseek-chat"}]
```

> 💡 **支持的 AI 服务商**：所有兼容 OpenAI Chat Completions 接口规范的服务均可使用，包括但不限于：
> - OpenAI (GPT-4o, GPT-4)
> - Anthropic Claude (通过 OpenAI 兼容网关)
> - DeepSeek (deepseek-chat)
> - 阿里通义千问 (qwen-turbo / qwen-plus)
> - 智谱 GLM (glm-4)
> - Moonshot (moonshot-v1)
> - 其他兼容 OpenAI 接口的服务

### 4. 启动服务

**方式一：Docker Compose（推荐）**

```bash
docker-compose up -d
```

**方式二：手动启动**

终端 1 — 后端：
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # 编辑 .env 填入 API Key
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

终端 2 — 前端：
```bash
cd frontend
npm install
npm run dev
```

### 5. 打开浏览器

访问 `http://localhost:5173`

## 使用流程

1. **输入章节**：粘贴或上传 ≥3 章小说文本
2. **选择模型**：在设置中选择 AI 模型（使用 .env 中配置的模型）
3. **一键转换**：AI 依次完成角色提取 → 场景拆分 → 剧本生成
4. **审阅编辑**：每步结果可查看、编辑、重新生成
5. **导出 YAML**：下载完整的结构化剧本 YAML 文件

## YAML 剧本格式

详见 [`docs/YAML_SCHEMA.md`](docs/YAML_SCHEMA.md)

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI 入口
│   │   ├── config.py           # 配置管理
│   │   ├── models/screenplay.py # 剧本 Pydantic 模型
│   │   ├── routes/             # API 路由
│   │   │   ├── upload.py       # 文件上传与解析
│   │   │   ├── convert.py      # AI 转换流水线
│   │   │   └── history.py      # 历史记录
│   │   ├── services/           # 业务逻辑
│   │   └── db/                 # 数据库
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/              # 页面组件
│   │   ├── components/         # 通用组件
│   │   ├── services/api.ts     # API 客户端
│   │   └── types/index.ts      # TypeScript 类型定义
│   ├── Dockerfile
│   └── package.json
├── docs/
│   └── YAML_SCHEMA.md          # YAML Schema 设计文档
├── docker-compose.yml
└── README.md
```

## License

MIT
