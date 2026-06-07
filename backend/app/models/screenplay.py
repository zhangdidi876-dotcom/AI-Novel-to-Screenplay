"""Pydantic 数据模型 — 剧本结构定义"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── 枚举类型 ──


class CharacterRole(str, Enum):
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MINOR = "minor"
    EXTRA = "extra"


class ElementType(str, Enum):
    ACTION = "action"
    DIALOGUE = "dialogue"
    PARENTHETICAL = "parenthetical"
    TRANSITION = "transition"
    SHOT = "shot"


# ── 嵌套子模型 ───


class Relationship(BaseModel):
    target: str = Field(..., description="目标角色 id")
    relation: str = Field(..., description="关系描述")


class SourceReference(BaseModel):
    chapter: int = Field(..., description="原文章节号")
    paragraphs: str = Field("", description="原文段落范围，如 '1-5'")


class ChapterSource(BaseModel):
    number: int
    title: str = ""


class ContentElement(BaseModel):
    element_type: ElementType = Field(..., description="元素类型")
    text: str = Field(..., description="内容文本")
    character_id: str = Field("", description="对白角色 id（仅 dialogue 类型，必填）")
    parenthetical: str = Field("", description="仅表演指示：低声/冷笑/愤怒/耳语等")


# ── 顶层模型 ───


class Meta(BaseModel):
    title: str = ""
    original_novel: str = ""
    original_author: str = ""
    adapted_by: str = ""
    version: str = "1.0.0"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    description: str = ""
    source_chapters: list[ChapterSource] = Field(default_factory=list)
    notes: str = ""


class Character(BaseModel):
    id: str = Field(..., description="唯一标识，如 char_001")
    name: str = Field(..., description="角色姓名")
    aliases: list[str] = Field(default_factory=list)
    role: CharacterRole = Field(default=CharacterRole.SUPPORTING)
    age: str = ""
    gender: str = ""
    occupation: str = ""
    description: str = ""
    traits: list[str] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    arc_summary: str = ""
    notes: str = ""


class Scene(BaseModel):
    id: str = Field(..., description="唯一标识，如 scene_001")
    scene_number: int = Field(..., ge=1)
    slug_line: str = Field("", description="场景标头，好莱坞标准: 'INT./EXT. 地点 - 时间'，如 'INT. 林家宅院 - 前厅 - 日'")
    characters_present: list[str] = Field(default_factory=list)
    summary: str = ""
    content: list[ContentElement] = Field(default_factory=list)
    transition: str = ""
    source_reference: Optional[SourceReference] = None
    notes: str = ""


class Screenplay(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    characters: list[Character] = Field(default_factory=list)
    scenes: list[Scene] = Field(default_factory=list)
