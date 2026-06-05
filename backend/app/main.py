"""FastAPI 应用入口"""

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.database import init_db
from .routes import upload, convert, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    await init_db()
    yield


app = FastAPI(
    title="AI 剧本创作工具",
    description="将小说章节转换为结构化剧本 YAML",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload.router, prefix="/api", tags=["文件上传"])
app.include_router(convert.router, prefix="/api", tags=["转换引擎"])
app.include_router(history.router, prefix="/api", tags=["历史记录"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/models")
async def list_models():
    """返回可用模型列表（仅展示名称，不暴露 API Key）"""
    models = [{"name": "默认模型", "model_name": settings.ai_model_name}]
    try:
        extra = json.loads(settings.ai_models_json)
        for m in extra:
            models.append({
                "name": m.get("name", "未命名"),
                "model_name": m.get("model_name", ""),
            })
    except (json.JSONDecodeError, TypeError):
        pass
    return {"models": models}
