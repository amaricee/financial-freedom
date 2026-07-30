from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _validate_refs(db: Session, account_id: int, category_id, account_id_tujuan):
    if not db.query(Account).filter(Account.id == account_id).first():
        raise HTTPException(status_code=400, detail="account_id tidak valid")
    if category_id and not db.query(Category).filter(Category.id == category_id).first():
        raise HTTPException(status_code=400, detail="category_id tidak valid")
    if account_id_tujuan and not db.query(Account).filter(Account.id == account_id_tujuan).first():
        raise HTTPException(status_code=400, detail="account_id_tujuan tidak valid")


@router.get("", response_model=List[TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    account_id: Optional[int] = None,
    category_id: Optional[int] = None,
    tipe: Optional[TransactionType] = None,
    tanggal_mulai: Optional[date] = Query(None),
    tanggal_akhir: Optional[date] = Query(None),
):
    q = db.query(Transaction)
    if account_id:
        q = q.filter(Transaction.account_id == account_id)
    if category_id:
        q = q.filter(Transaction.category_id == category_id)
    if tipe:
        q = q.filter(Transaction.tipe == tipe)
    if tanggal_mulai:
        q = q.filter(Transaction.tanggal >= tanggal_mulai)
    if tanggal_akhir:
        q = q.filter(Transaction.tanggal <= tanggal_akhir)
    return q.order_by(Transaction.tanggal.desc(), Transaction.id.desc()).all()


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    trx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not trx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    return trx


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    _validate_refs(db, payload.account_id, payload.category_id, payload.account_id_tujuan)
    trx = Transaction(**payload.model_dump())
    db.add(trx)
    db.commit()
    db.refresh(trx)
    return trx


@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)):
    trx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not trx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    data = payload.model_dump(exclude_unset=True)
    _validate_refs(
        db,
        data.get("account_id", trx.account_id),
        data.get("category_id", trx.category_id),
        data.get("account_id_tujuan", trx.account_id_tujuan),
    )
    for field, value in data.items():
        setattr(trx, field, value)
    db.commit()
    db.refresh(trx)
    return trx


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    trx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not trx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    db.delete(trx)
    db.commit()
