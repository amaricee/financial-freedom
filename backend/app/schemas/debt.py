from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.debt import DebtType, DebtStatus


class DebtBase(BaseModel):
    tipe: DebtType
    nama_pihak: str
    jumlah_total: Decimal
    tanggal: date
    jatuh_tempo: Optional[date] = None
    notes: Optional[str] = None


class DebtCreate(DebtBase):
    pass


class DebtUpdate(BaseModel):
    nama_pihak: Optional[str] = None
    jumlah_total: Optional[Decimal] = None
    jatuh_tempo: Optional[date] = None
    notes: Optional[str] = None


class DebtOut(DebtBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    jumlah_terbayar: Decimal
    status: DebtStatus
    created_at: datetime
    updated_at: Optional[datetime] = None


class DebtPayment(BaseModel):
    """Payload buat bayar/terima cicilan hutang-piutang."""

    jumlah: Decimal
    account_id: int  # akun yang dipakai buat bayar/nerima
    tanggal: date
    deskripsi: Optional[str] = None