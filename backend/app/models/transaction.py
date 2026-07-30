import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Enum,
    Date,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"
    transfer = "transfer"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    tipe = Column(Enum(TransactionType), nullable=False)
    jumlah = Column(Numeric(15, 2), nullable=False)
    tanggal = Column(Date, nullable=False)
    deskripsi = Column(String(255), nullable=True)

    # Khusus tipe = transfer: akun tujuan
    account_id_tujuan = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    # Khusus transaksi hasil pembayaran hutang/piutang (diisi otomatis)
    debt_id = Column(Integer, ForeignKey("debts.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    account = relationship("Account", foreign_keys=[account_id])
    account_tujuan = relationship("Account", foreign_keys=[account_id_tujuan])
    category = relationship("Category")
