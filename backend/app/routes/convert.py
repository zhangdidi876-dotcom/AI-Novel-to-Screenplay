"""AI 转换流水线路由"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ConvertRequest(BaseModel):
    text: str  # 章节原文
    model_index: int = 0  # 模型索引（0=默认模型）


@router.post("/extract/characters")
async def extract_characters(req: ConvertRequest):
    """提取角色"""
    # TODO: Day 2 实现
    return {"characters": [], "message": "待实现"}


@router.post("/extract/scenes")
async def extract_scenes(req: ConvertRequest):
    """拆分场景"""
    # TODO: Day 2 实现
    return {"scenes": [], "message": "待实现"}


@router.post("/generate/script")
async def generate_script(req: ConvertRequest):
    """生成剧本"""
    # TODO: Day 2 实现
    return {"screenplay": {}, "message": "待实现"}
