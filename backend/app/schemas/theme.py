"""主题/外观 API 的 Pydantic 模型。"""
from typing import Any, Optional

from pydantic import BaseModel


class ThemeResponse(BaseModel):
    data: Optional[Any] = None


class ThemeUpdate(BaseModel):
    data: Any


class ImageUploadResponse(BaseModel):
    id: int
