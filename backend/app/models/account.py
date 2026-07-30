import enum

from sqlalchemy import Column, Integer, String, Numeric, Enum, DateTime, func

from app.core.database import Base


class AccountType(str, enum.Enum):
    bank = "bank"
    cash = "cash"
    e_wallet = "e_wallet"
    investasi = "investasi"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    tipe = Column(Enum(AccountType), nullable=False, default=AccountType.bank)
    saldo_awal = Column(Numeric(15, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="IDR")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
