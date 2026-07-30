from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.category import CategoryType


class CategoryBase(BaseModel):
    nama: str
    tipe: CategoryType
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    nama: Optional[str] = None
    tipe: Optional[CategoryType] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class CategoryTree(CategoryOut):
    """Response nested, dengan daftar sub-kategori di dalamnya."""

    children: List["CategoryTree"] = []


CategoryTree.model_rebuild()
