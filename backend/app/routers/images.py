import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..config import BASE_DIR
from ..deps import current_user_id

router = APIRouter(prefix="/api", tags=["images"])

UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/images")
async def upload_image(
    file: UploadFile = File(...),
    user_id: int = Depends(current_user_id),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, "不支持的图片格式")
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "图片过大（最大 5MB）")
    filename = f"{uuid.uuid4().hex}{ext}"
    (UPLOAD_DIR / filename).write_bytes(content)
    return {"url": f"/uploads/{filename}"}
