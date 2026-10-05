"""主题/外观 API。

- GET  /api/theme          取主题状态 JSON（无则返回 {"data": null}）
- PUT  /api/theme          覆盖保存主题状态 JSON
- POST /api/theme/image    上传背景图，返回 {"id": <int>}
- GET  /api/theme/image/{id}  取背景图（long-cache，内容按 id 寻址）
- DELETE /api/theme/image/{id} 删除背景图

背景图以文件形式落在 DATA_DIR/images/<id>，元数据存 background_image 表，
因此设置与图片都跟随「同一份后端」，换浏览器/换机器只要指到同一服务即可跟随。
"""
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.config import DATA_DIR
from ..models.theme import ThemeSetting, BackgroundImage
from ..schemas.theme import ThemeResponse, ThemeUpdate, ImageUploadResponse

router = APIRouter(prefix="/api/theme", tags=["主题/外观"])

IMAGES_DIR = DATA_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

MAX_IMAGE_BYTES = 25 * 1024 * 1024  # 25MB


@router.get("", response_model=ThemeResponse)
def get_theme(db: Session = Depends(get_db)):
    s = db.query(ThemeSetting).filter(ThemeSetting.id == 1).first()
    if not s or not s.data:
        return ThemeResponse(data=None)
    try:
        return ThemeResponse(data=json.loads(s.data))
    except Exception:
        return ThemeResponse(data=None)


@router.put("", response_model=ThemeResponse)
def put_theme(payload: ThemeUpdate, db: Session = Depends(get_db)):
    s = db.query(ThemeSetting).filter(ThemeSetting.id == 1).first()
    if not s:
        s = ThemeSetting(id=1)
        db.add(s)
    s.data = json.dumps(payload.data, ensure_ascii=False)
    db.commit()
    db.refresh(s)
    return ThemeResponse(data=payload.data)


@router.post("/image", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    blob = await file.read()
    if len(blob) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="图片过大（>25MB）")
    row = BackgroundImage(mime=file.content_type or "image/jpeg")
    db.add(row)
    db.commit()
    db.refresh(row)
    path = IMAGES_DIR / str(row.id)
    path.write_bytes(blob)
    return ImageUploadResponse(id=row.id)


@router.get("/image/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)):
    row = db.query(BackgroundImage).filter(BackgroundImage.id == image_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    path = IMAGES_DIR / str(image_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(
        str(path),
        media_type=row.mime or "image/jpeg",
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )


@router.delete("/image/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    row = db.query(BackgroundImage).filter(BackgroundImage.id == image_id).first()
    if row:
        db.delete(row)
        db.commit()
    path = IMAGES_DIR / str(image_id)
    try:
        path.unlink()
    except FileNotFoundError:
        pass
    return {"ok": True}
