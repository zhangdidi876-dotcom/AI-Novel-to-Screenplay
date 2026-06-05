"""FastAPI 应用入口"""

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
