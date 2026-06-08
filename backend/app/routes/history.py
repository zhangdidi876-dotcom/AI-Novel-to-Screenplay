"""转换历史记录路由"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update as sql_update

from ..db.database import get_db
from ..db.models import ConversionHistory

router = APIRouter()


@router.get("/history")
async def list_history(db: AsyncSession = Depends(get_db)):
    """获取转换历史列表"""
    result = await db.execute(
        select(ConversionHistory).order_by(desc(ConversionHistory.created_at)).limit(100)
    )
    records = result.scalars().all()
    return {
        "history": [
            {
                "id": r.id,
                "session_id": r.session_id,
                "title": r.title,
                "chapter_count": r.chapter_count,
                "model_name": r.model_name,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else "",
            }
            for r in records
        ]
    }


@router.get("/history/{record_id}")
async def get_history_detail(record_id: int, db: AsyncSession = Depends(get_db)):
    """获取单条历史记录详情"""
    result = await db.execute(
        select(ConversionHistory).where(ConversionHistory.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        return {"error": "记录不存在"}
    return {
        "id": record.id,
        "session_id": record.session_id,
        "title": record.title,
        "chapter_count": record.chapter_count,
        "model_name": record.model_name,
        "input_text": record.input_text,
        "output_yaml": record.output_yaml,
        "status": record.status,
        "created_at": record.created_at.isoformat() if record.created_at else "",
    }


class RenameRequest(BaseModel):
    title: str


@router.patch("/history/{record_id}/rename")
async def rename_history(record_id: int, req: RenameRequest, db: AsyncSession = Depends(get_db)):
    """重命名历史记录"""
    await db.execute(
        sql_update(ConversionHistory)
        .where(ConversionHistory.id == record_id)
        .values(title=req.title)
    )
    await db.commit()
    return {"status": "ok"}


@router.delete("/history/{record_id}")
async def delete_history(record_id: int, db: AsyncSession = Depends(get_db)):
    """删除历史记录"""
    result = await db.execute(
        select(ConversionHistory).where(ConversionHistory.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        return {"error": "记录不存在"}
    await db.delete(record)
    await db.commit()
    return {"status": "deleted", "id": record_id}
