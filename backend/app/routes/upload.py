"""文件上传与解析路由"""

import re

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

ALLOWED_EXTENSIONS = {".txt", ".docx", ".pdf", ".md", ".markdown"}


@router.post("/upload")
async def upload_chapter(file: UploadFile = File(...)):
    """上传章节文件，返回解析后的纯文本"""
    ext = file.filename.lower()
    dot_index = ext.rfind(".")
    ext = ext[dot_index:] if dot_index >= 0 else ""

    if ext not in ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={"error": f"不支持的文件格式: {ext}，支持: {', '.join(ALLOWED_EXTENSIONS)}"},
        )

    raw = await file.read()

    if ext in (".txt", ".md", ".markdown"):
        text = raw.decode("utf-8", errors="replace")
    elif ext == ".docx":
        text = parse_docx(raw)
    elif ext == ".pdf":
        text = parse_pdf(raw)
    else:
        text = ""

    return {
        "filename": file.filename,
        "text": text,
        "char_count": len(text),
    }


@router.post("/upload/text")
async def upload_text(text: str = Form(...)):
    """直接粘贴文本"""
    return {
        "filename": "paste.txt",
        "text": text,
        "char_count": len(text),
    }


# ── 智能章节检测 ──────────────────────────────────────────

# 用于清洗标题中已存在的章节标记
STRIP_TITLE_RE = re.compile(
    r'^\s*(第\s*[一二三四五六七八九十百千0-9]+\s*[章节回卷集部篇]\s*|Chapter\s+\d+\s*|Part\s+\d+\s*)+'
    r'[：:.\s、。，,!！?？]*'
)


def _strip_title(raw_title: str) -> str:
    """移除标题中已有的章节标记，避免重复"""
    return STRIP_TITLE_RE.sub("", raw_title).strip()


CHAPTER_PATTERNS = [
    # 中文: 第X章 / 第X回 / 第X卷 / 第X节
    re.compile(r'^[  \t]*第\s*[一二三四五六七八九十百千0-9]+\s*[章节回卷集部篇]', re.MULTILINE),
    # 英文: Chapter X / Part X
    re.compile(r'^[  \t]*Chapter\s+\d+', re.MULTILINE | re.IGNORECASE),
    re.compile(r'^[  \t]*Part\s+\d+', re.MULTILINE | re.IGNORECASE),
    # 纯数字标题: 1. / 1、/ 一、
    re.compile(r'^[  \t]*\d+[\.\、\s]+[^\d]', re.MULTILINE),
    # 卷/回
    re.compile(r'^[  \t]*[卷回]\s*[一二三四五六七八九十百千0-9]+', re.MULTILINE),
]


def _detect_chapters_regex(text: str) -> list[dict]:
    """用正则表达式检测章节边界"""
    # 尝试找出所有可能的章节起始位置
    positions: list[int] = []
    seen = set()
    for pat in CHAPTER_PATTERNS:
        for m in pat.finditer(text):
            pos = m.start()
            if pos not in seen:
                positions.append(pos)
                seen.add(pos)
    positions.sort()

    if len(positions) < 2:
        return []

    # 按位置拆分章节
    chapters = []
    for i, pos in enumerate(positions):
        start = pos
        end = positions[i + 1] if i + 1 < len(positions) else len(text)
        raw = text[start:end].strip()
        # 提取标题（第一行），正文内容去除标题行避免重复
        first_line_end = raw.find("\n")
        if first_line_end > 0:
            title = _strip_title(raw[:first_line_end].strip())
            content = raw[first_line_end:].strip()
        else:
            title = _strip_title(raw[:50])
            content = raw
        chapters.append({
            "number": i + 1,
            "title": title,
            "content": content,
        })
    return chapters


class DetectRequest(BaseModel):
    text: str


@router.post("/detect/chapters")
async def detect_chapters(req: DetectRequest):
    """智能检测章节边界 — 先用正则，失败时返回建议"""
    text = req.text.strip()
    if len(text) < 100:
        return {"chapters": [], "method": "none", "message": "文本太短"}

    chapters = _detect_chapters_regex(text)
    if len(chapters) >= 2:
        return {
            "chapters": chapters,
            "chapter_count": len(chapters),
            "method": "regex",
        }

    # 正则没找到 → 返回空，前端提示用 AI
    return {
        "chapters": [],
        "chapter_count": 0,
        "method": "none",
        "message": "未检测到章节标记，请使用「AI识别」",
    }


@router.post("/detect/chapters/ai")
async def detect_chapters_ai(req: DetectRequest):
    """用 AI 检测章节边界（适用于无明确标记的小说文本）"""
    from ..services.ai_client import AIClient, default_client

    text = req.text.strip()
    if len(text) < 100:
        return {"chapters": [], "method": "ai", "message": "文本太短"}

    # 只取前8000字让AI分析结构
    sample = text[:8000] if len(text) > 8000 else text
    prompt = f"""分析以下小说文本，找出所有章节边界位置。

返回 JSON 格式：
{{"breaks": [100, 520, 980]}}

其中 breaks 数组是每章开始位置的字符索引（从0开始计数）。

常见章节标记：
- "第X章"、"第X回"、"Chapter X"
- 大段空行（3行以上）
- 序号标题（一、/ 1. / (1)）
- 明显的场景切换

如果没有明显章节边界，返回 breaks: []。

文本：
{sample}
"""
    client = default_client
    try:
        response = await client.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000,
            json_mode=True,
        )
        data = client.parse_json(response)
        breaks = data.get("breaks", [])
        if not breaks or len(breaks) < 2:
            return {"chapters": [], "method": "ai", "message": "AI 未检测到明显章节边界"}

        # 根据AI给的索引切分全文
        breaks.sort()
        chapters = []
        for i in range(len(breaks)):
            start = breaks[i]
            end = breaks[i + 1] if i + 1 < len(breaks) else len(text)
            raw = text[start:end].strip()
            first_line_end = raw.find("\n")
            if first_line_end > 0:
                title = _strip_title(raw[:first_line_end].strip())
                content = raw[first_line_end:].strip()
            else:
                title = _strip_title(raw[:50])
                content = raw
            chapters.append({
                "number": i + 1,
                "title": title,
                "content": content,
            })
        return {
            "chapters": chapters,
            "chapter_count": len(chapters),
            "method": "ai",
        }
    except Exception as e:
        return {"chapters": [], "method": "ai", "error": str(e)}


# ── 文件解析器 ────────────────────────────────────────────


def parse_docx(raw: bytes) -> str:
    """解析 .docx 文件为纯文本"""
    from io import BytesIO
    from docx import Document

    doc = Document(BytesIO(raw))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def parse_pdf(raw: bytes) -> str:
    """解析 .pdf 文件为纯文本"""
    from io import BytesIO
    from PyPDF2 import PdfReader

    reader = PdfReader(BytesIO(raw))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)
