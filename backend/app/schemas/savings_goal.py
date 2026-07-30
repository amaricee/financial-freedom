from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SavingsGoalBase(BaseModel):
    nama: str
    target_jumlah: Decimal
    current_jumlah: Decimal = Decimal("0")
    target_tanggal: Optional[date] = None
    account_id: Optional[int] = None


class SavingsGoalCreate(SavingsGoalBase):
    pass


class SavingsGoalUpdate(BaseModel):
    nama: Optional[str] = None
    target_jumlah: Optional[Decimal] = None
    current_jumlah: Optional[Decimal] = None
    target_tanggal: Optional[date] = None
    account_id: Optional[int] = None


class SavingsGoalOut(SavingsGoalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class SavingsGoalContribution(BaseModel):
    """Payload buat nambah tabungan ke goal (bukan replace current_jumlah langsung)."""

    jumlah: Decimal