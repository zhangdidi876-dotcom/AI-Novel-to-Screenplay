"""文件上传与解析路由"""

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".txt", ".docx", ".pdf"}


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

    if ext == ".txt":
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
