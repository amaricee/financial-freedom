from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BudgetBase(BaseModel):
    category_id: int
    bulan: int = Field(ge=1, le=12)
    tahun: int
    jumlah_budget: Decimal


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    jumlah_budget: Optional[Decimal] = None


class BudgetOut(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class BudgetWithRealisasi(BudgetOut):
    """Realisasi = total transaksi expense kategori ini di bulan/tahun tsb."""

    realisasi: Decimal
    sisa: Decimal
    persentase: float