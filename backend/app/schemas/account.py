from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.account import AccountType


class AccountBase(BaseModel):
    nama: str
    tipe: AccountType
    saldo_awal: Decimal = Decimal("0")
    currency: str = "IDR"


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    nama: Optional[str] = None
    tipe: Optional[AccountType] = None
    saldo_awal: Optional[Decimal] = None
    currency: Optional[str] = None


class AccountOut(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class AccountWithBalance(AccountOut):
    """Response yang udah termasuk saldo_current hasil kalkulasi on-the-fly."""

    saldo_current: Decimal
