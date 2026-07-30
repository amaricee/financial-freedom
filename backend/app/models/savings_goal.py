from datetime import date as date_type

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    target_jumlah = Column(Numeric(15, 2), nullable=False)
    current_jumlah = Column(Numeric(15, 2), nullable=False, default=0)
    target_tanggal = Column(Date, nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    account = relationship("Account")