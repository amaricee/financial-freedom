from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.transaction import TransactionType


class TransactionFields(BaseModel):
    """Field dasar, dipakai bareng oleh Create dan Out, TANPA validasi bisnis."""

    account_id: int
    category_id: Optional[int] = None
    tipe: TransactionType
    jumlah: Decimal
    tanggal: date
    deskripsi: Optional[str] = None
    account_id_tujuan: Optional[int] = None


class TransactionCreate(TransactionFields):
    """Dipakai khusus untuk request body POST/PUT — validasi bisnis di sini."""

    @model_validator(mode="after")
    def validate_by_tipe(self):
        if self.tipe == TransactionType.transfer:
            if not self.account_id_tujuan:
                raise ValueError("account_id_tujuan wajib diisi untuk transaksi transfer")
            if self.account_id_tujuan == self.account_id:
                raise ValueError("Akun sumber dan akun tujuan transfer tidak boleh sama")
        else:
            if not self.category_id:
                raise ValueError("category_id wajib diisi untuk transaksi income/expense")
        return self


class TransactionUpdate(BaseModel):
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    tipe: Optional[TransactionType] = None
    jumlah: Optional[Decimal] = None
    tanggal: Optional[date] = None
    deskripsi: Optional[str] = None
    account_id_tujuan: Optional[int] = None


class TransactionOut(TransactionFields):
    """Dipakai untuk response — TIDAK ada validasi bisnis, karena transaksi hasil
    pembayaran hutang/piutang boleh punya category_id null walau tipe-nya expense/income."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None