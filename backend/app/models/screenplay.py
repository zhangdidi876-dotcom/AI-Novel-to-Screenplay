"""Pydantic 数据模型 — 剧本结构定义"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── 枚举类型 ─────────────────────────────────────────────


class CharacterRole(str, Enum):
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MINOR = "minor"
    EXTRA = "extra"


class SceneTime(str, Enum):
    DAY = "day"
    NIGHT = "night"
    DAWN = "dawn"
    DUSK = "dusk"
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    CONTINUOUS = "continuous"
    LATER = "later"
    SAME = "same"


class ElementType(str, Enum):
    ACTION = "action"
    DIALOGUE = "dialogue"
    PARENTHETICAL = "parenthetical"
    TRANSITION = "transition"
    SHOT = "shot"


# ── 嵌套子模型 ───────────────────────────────────────────


class Relationship(BaseModel):
    target: str = Field(..., description="目标角色 id")
    relation: str = Field(..., description="关系描述")


class SourceReference(BaseModel):
    chapter: int = Field(..., description="原文章节号")
    paragraphs: list[int] = Field(default_factory=list, description="原文段落范围")


class ChapterSource(BaseModel):
    number: int
    title: str = ""


class SlugLine(BaseModel):
    location: str = Field(..., description="地点描述")
    time: SceneTime = Field(..., description="时间")
    set_details: str = Field("", description="场景补充描述")


class ContentElement(BaseModel):
    element_type: ElementType = Field(..., description="元素类型")
    text: str = Field(..., description="内容文本")
    character_id: str = Field("", description="对白角色 id（仅 dialogue 类型）")
    parenthetical: str = Field("", description="对白括号备注")


# ── 顶层模型 ─────────────────────────────────────────────


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
    slug_line: SlugLine
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
