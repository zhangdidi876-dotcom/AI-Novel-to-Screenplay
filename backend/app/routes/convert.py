"""AI 转换流水线路由 — 角色提取 → 场景拆分 → 剧本生成 → YAML 导出"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db.database import get_db
from ..db.models import ConversionHistory
from ..services.ai_client import AIClient
from ..services.character import extract_characters as do_extract_characters
from ..services.scene import extract_scenes as do_extract_scenes
from ..services.script import generate_script as do_generate_script
from ..services.yaml_export import screenplay_to_yaml, yaml_to_screenplay

logger = logging.getLogger(__name__)
router = APIRouter()


class ConvertRequest(BaseModel):
    text: str
    model_index: int = 0
    session_id: str = ""


class SaveRequest(BaseModel):
    session_id: str = ""
    title: str
    chapter_count: int
    model_name: str
    input_text: str
    output_yaml: str
    status: str = "running"  # running / partial / completed


class ExportRequest(BaseModel):
    screenplay: dict
    title: str = ""


class ValidateRequest(BaseModel):
    yaml_text: str


def _get_client(model_index: int = 0) -> AIClient:
    """根据索引获取 AI 客户端，支持多模型切换"""
    if model_index == 0:
        return AIClient()
    try:
        models = json.loads(settings.ai_models_json)
        if model_index - 1 < len(models):
            m = models[model_index - 1]
            return AIClient(
                base_url=m.get("base_url", settings.ai_base_url),
                api_key=m.get("api_key", settings.ai_api_key),
                model_name=m.get("model_name", settings.ai_model_name),
            )
    except (json.JSONDecodeError, IndexError):
        pass
    return AIClient()


async def _save_history(session_id: str, text: str, status: str, yaml: str = "", db=None):
    """后端自动保存转换历史"""
    if not session_id or db is None:
        return
    import re
    from sqlalchemy import update as sql_update
    ch_match = re.findall(r'(第\s*[一二三四五六七八九十百千0-9]+\s*章|Chapter\s+\d+)', text)
    chapter_count = len(ch_match)
    result = await db.execute(
        select(ConversionHistory).where(ConversionHistory.session_id == session_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        values = {"status": status, "updated_at": func.now()}
        if yaml: values["output_yaml"] = yaml
        await db.execute(
            sql_update(ConversionHistory).where(ConversionHistory.session_id == session_id).values(**values)
        )
    else:
        db.add(ConversionHistory(
            session_id=session_id, title="未命名项目",
            chapter_count=chapter_count, model_name="",
            input_text=text[:500], output_yaml=yaml, status=status,
        ))
    await db.commit()


# ── 分步端点 ─────────────────────────────────────────────


@router.post("/extract/characters")
async def extract_characters(
    req: ConvertRequest,
    db: AsyncSession = Depends(get_db),
):
    """步骤1：从章节文本中提取角色列表"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="章节文本不能为空")

    await _save_history(req.session_id, req.text, "running", db=db)
    try:
        client = _get_client(req.model_index)
        characters = await do_extract_characters(req.text, client)
        await _save_history(req.session_id, req.text, "partial", db=db)
    except Exception as e:
        await _save_history(req.session_id, req.text, "interrupted", db=db)
        logger.error(f"角色提取失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {e}")

    return {"characters": characters, "count": len(characters)}


@router.post("/extract/scenes")
async def extract_scenes(
    req: ConvertRequest,
    db: AsyncSession = Depends(get_db),
):
    """步骤2：先提取角色，再拆分为场景"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="章节文本不能为空")

    await _save_history(req.session_id, req.text, "running", db=db)
    try:
        client = _get_client(req.model_index)
        characters = await do_extract_characters(req.text, client)
        scenes = await do_extract_scenes(req.text, characters, client)
        await _save_history(req.session_id, req.text, "partial", db=db)
    except Exception as e:
        await _save_history(req.session_id, req.text, "interrupted", db=db)
        logger.error(f"场景拆分失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {e}")

    return {"characters": characters, "scenes": scenes, "scene_count": len(scenes)}


@router.post("/generate/script")
async def generate_script(
    req: ConvertRequest,
    db: AsyncSession = Depends(get_db),
):
    """步骤3：完整流程 — 角色提取 + 场景拆分 + 剧本内容生成"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="章节文本不能为空")

    await _save_history(req.session_id, req.text, "running", db=db)
    try:
        client = _get_client(req.model_index)
        characters = await do_extract_characters(req.text, client)
        await _save_history(req.session_id, req.text, "partial", db=db)
        scenes = await do_extract_scenes(req.text, characters, client)
        script_scenes = await do_generate_script(req.text, characters, scenes, client)
        for i, scene in enumerate(scenes):
            if i < len(script_scenes):
                scene["content"] = script_scenes[i].get("content", [])
    except Exception as e:
        await _save_history(req.session_id, req.text, "interrupted", db=db)
        logger.error(f"剧本生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI 调用失败: {e}")

    screenplay = {
        "meta": {
            "title": "",
            "original_novel": "",
            "original_author": "",
            "adapted_by": "AI 辅助改编",
            "version": "1.0.0",
            "description": "",
            "source_chapters": [],
            "notes": "",
        },
        "characters": characters,
        "scenes": scenes,
    }

    return {"screenplay": screenplay}


@router.post("/convert/full")
async def convert_full(
    req: ConvertRequest,
    db: AsyncSession = Depends(get_db),
):
    """一键全流程转换"""
    return await generate_script(req, db=db)


# ── YAML 导出与校验 ─────────────────────────────────────


@router.post("/export/yaml")
async def export_yaml(req: ExportRequest):
    """将 screenplay 对象导出为 YAML 字符串"""
    if req.title:
        req.screenplay.setdefault("meta", {})["title"] = req.title
    yaml_str = screenplay_to_yaml(req.screenplay)
    return {"yaml": yaml_str}


@router.post("/validate/yaml")
async def validate_yaml(req: ValidateRequest):
    """校验 YAML 字符串是否符合剧本 Schema"""
    try:
        data = yaml_to_screenplay(req.yaml_text)
    except Exception as e:
        return {"valid": False, "error": f"YAML 解析失败: {e}"}

    errors = []
    for required in ["meta", "characters", "scenes"]:
        if required not in data:
            errors.append(f"缺少 {required} 块")

    for i, scene in enumerate(data.get("scenes", [])):
        for field in ["scene_number", "slug_line", "content"]:
            if field not in scene:
                errors.append(f"场景 {i+1} 缺少 {field}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "character_count": len(data.get("characters", [])),
        "scene_count": len(data.get("scenes", [])),
    }


# ── 历史记录保存 ────────────────────────────────────────


@router.post("/history/save")
async def save_history(req: SaveRequest, db: AsyncSession = Depends(get_db)):
    """保存/更新转换结果（按 session_id upsert）"""
    from sqlalchemy import update as sql_update

    if req.session_id:
        result = await db.execute(
            select(ConversionHistory).where(ConversionHistory.session_id == req.session_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            # 更新已有记录
            await db.execute(
                sql_update(ConversionHistory)
                .where(ConversionHistory.session_id == req.session_id)
                .values(
                    title=req.title or existing.title,
                    chapter_count=req.chapter_count or existing.chapter_count,
                    model_name=req.model_name or existing.model_name,
                    input_text=req.input_text or existing.input_text,
                    output_yaml=req.output_yaml or existing.output_yaml,
                    status=req.status,
                    updated_at=func.now(),
                )
            )
            await db.commit()
            return {"id": existing.id, "status": "updated", "session_id": req.session_id}

    # 新建
    record = ConversionHistory(
        session_id=req.session_id,
        title=req.title,
        chapter_count=req.chapter_count,
        model_name=req.model_name,
        input_text=req.input_text,
        output_yaml=req.output_yaml,
        status=req.status,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return {"id": record.id, "status": "created", "session_id": req.session_id}
