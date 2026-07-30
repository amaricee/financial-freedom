import enum

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class CategoryType(str, enum.Enum):
    income = "income"
    expense = "expense"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    tipe = Column(Enum(CategoryType), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Self-referencing relationship buat sub-kategori
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent")
