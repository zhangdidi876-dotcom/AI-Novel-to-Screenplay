"""SQLAlchemy ORM 模型 — 转换历史记录"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class ConversionHistory(Base):
    __tablename__ = "conversion_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(default="未命名项目")
    chapter_count: Mapped[int] = mapped_column(default=0)
    model_name: Mapped[str] = mapped_column(default="")
    input_text: Mapped[str] = mapped_column(Text, default="")
    output_yaml: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
