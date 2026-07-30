from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.schemas.account import AccountCreate, AccountUpdate, AccountOut, AccountWithBalance

router = APIRouter(prefix="/accounts", tags=["Accounts"])


def _hitung_saldo_current(db: Session, account: Account) -> Decimal:
    """
    saldo_current = saldo_awal
      + total income masuk ke akun ini
      - total expense keluar dari akun ini
      - total transfer keluar dari akun ini
      + total transfer masuk ke akun ini (dari akun lain)
    """
    income = (
        db.query(func.coalesce(func.sum(Transaction.jumlah), 0))
        .filter(Transaction.account_id == account.id, Transaction.tipe == TransactionType.income)
        .scalar()
    )
    expense = (
        db.query(func.coalesce(func.sum(Transaction.jumlah), 0))
        .filter(Transaction.account_id == account.id, Transaction.tipe == TransactionType.expense)
        .scalar()
    )
    transfer_keluar = (
        db.query(func.coalesce(func.sum(Transaction.jumlah), 0))
        .filter(Transaction.account_id == account.id, Transaction.tipe == TransactionType.transfer)
        .scalar()
    )
    transfer_masuk = (
        db.query(func.coalesce(func.sum(Transaction.jumlah), 0))
        .filter(
            Transaction.account_id_tujuan == account.id,
            Transaction.tipe == TransactionType.transfer,
        )
        .scalar()
    )
    return account.saldo_awal + income - expense - transfer_keluar + transfer_masuk


@router.get("", response_model=List[AccountWithBalance])
def list_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return [
        AccountWithBalance(
            **AccountOut.model_validate(acc).model_dump(),
            saldo_current=_hitung_saldo_current(db, acc),
        )
        for acc in accounts
    ]


@router.get("/{account_id}", response_model=AccountWithBalance)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Akun tidak ditemukan")
    return AccountWithBalance(
        **AccountOut.model_validate(account).model_dump(),
        saldo_current=_hitung_saldo_current(db, account),
    )


@router.post("", response_model=AccountOut, status_code=201)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    account = Account(**payload.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.put("/{account_id}", response_model=AccountOut)
def update_account(account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Akun tidak ditemukan")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Akun tidak ditemukan")

    has_transaction = (
        db.query(Transaction)
        .filter(
            (Transaction.account_id == account_id)
            | (Transaction.account_id_tujuan == account_id)
        )
        .first()
    )
    if has_transaction:
        raise HTTPException(
            status_code=400,
            detail="Akun tidak bisa dihapus karena masih punya transaksi terkait",
        )

    db.delete(account)
    db.commit()
