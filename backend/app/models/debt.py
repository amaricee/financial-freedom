import enum

from sqlalchemy import Column, Integer, String, Numeric, Date, Enum, Text, DateTime, func

from app.core.database import Base


class DebtType(str, enum.Enum):
    hutang = "hutang"      # saya berhutang ke orang
    piutang = "piutang"    # orang berhutang ke saya


class DebtStatus(str, enum.Enum):
    belum_lunas = "belum_lunas"
    lunas = "lunas"


class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    tipe = Column(Enum(DebtType), nullable=False)
    nama_pihak = Column(String(100), nullable=False)
    jumlah_total = Column(Numeric(15, 2), nullable=False)
    jumlah_terbayar = Column(Numeric(15, 2), nullable=False, default=0)
    tanggal = Column(Date, nullable=False)
    jatuh_tempo = Column(Date, nullable=True)
    status = Column(Enum(DebtStatus), nullable=False, default=DebtStatus.belum_lunas)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())