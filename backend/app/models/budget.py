from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("category_id", "bulan", "tahun", name="uq_budget_category_periode"),
    )

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    bulan = Column(Integer, nullable=False)  # 1-12
    tahun = Column(Integer, nullable=False)
    jumlah_budget = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("Category")