from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.account import Account
from app.models.debt import Debt, DebtType, DebtStatus
from app.models.transaction import Transaction, TransactionType
from app.schemas.debt import DebtCreate, DebtUpdate, DebtOut, DebtPayment

router = APIRouter(prefix="/debts", tags=["Debts"])


@router.get("", response_model=List[DebtOut])
def list_debts(
    db: Session = Depends(get_db),
    tipe: Optional[DebtType] = None,
    status: Optional[DebtStatus] = None,
):
    q = db.query(Debt)
    if tipe:
        q = q.filter(Debt.tipe == tipe)
    if status:
        q = q.filter(Debt.status == status)
    # MariaDB/MySQL gak support NULLS LAST, jadi manual pakai CASE:
    # data tanpa jatuh_tempo (NULL) diurutkan paling belakang
    return q.order_by(
        case((Debt.jatuh_tempo.is_(None), 1), else_=0),
        Debt.jatuh_tempo.asc(),
    ).all()


@router.get("/{debt_id}", response_model=DebtOut)
def get_debt(debt_id: int, db: Session = Depends(get_db)):
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Data hutang/piutang tidak ditemukan")
    return debt


@router.post("", response_model=DebtOut, status_code=201)
def create_debt(payload: DebtCreate, db: Session = Depends(get_db)):
    debt = Debt(**payload.model_dump(), jumlah_terbayar=0, status=DebtStatus.belum_lunas)
    db.add(debt)
    db.commit()
    db.refresh(debt)
    return debt


@router.put("/{debt_id}", response_model=DebtOut)
def update_debt(debt_id: int, payload: DebtUpdate, db: Session = Depends(get_db)):
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Data hutang/piutang tidak ditemukan")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(debt, field, value)
    db.commit()
    db.refresh(debt)
    return debt


@router.post("/{debt_id}/payments", response_model=DebtOut)
def pay_debt(debt_id: int, payload: DebtPayment, db: Session = Depends(get_db)):
    """
    Catat pembayaran/pelunasan hutang atau piutang.
    - tipe = hutang   -> kita bayar orang -> expense dari account_id
    - tipe = piutang  -> orang bayar kita -> income ke account_id
    Otomatis bikin Transaction terkait (debt_id terisi) dan update jumlah_terbayar + status.
    """
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Data hutang/piutang tidak ditemukan")
    if debt.status == DebtStatus.lunas:
        raise HTTPException(status_code=400, detail="Hutang/piutang ini sudah lunas")

    if payload.jumlah <= 0:
        raise HTTPException(status_code=400, detail="Jumlah pembayaran harus lebih dari 0")

    sisa = debt.jumlah_total - debt.jumlah_terbayar
    if payload.jumlah > sisa:
        raise HTTPException(
            status_code=400,
            detail=f"Jumlah pembayaran melebihi sisa tagihan ({sisa})",
        )

    account = db.query(Account).filter(Account.id == payload.account_id).first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id tidak valid")

    trx_tipe = TransactionType.expense if debt.tipe == DebtType.hutang else TransactionType.income
    default_desc = (
        f"Pembayaran hutang ke {debt.nama_pihak}"
        if debt.tipe == DebtType.hutang
        else f"Pelunasan piutang dari {debt.nama_pihak}"
    )

    trx = Transaction(
        account_id=payload.account_id,
        category_id=None,
        tipe=trx_tipe,
        jumlah=payload.jumlah,
        tanggal=payload.tanggal,
        deskripsi=payload.deskripsi or default_desc,
        debt_id=debt.id,
    )
    db.add(trx)

    debt.jumlah_terbayar = debt.jumlah_terbayar + payload.jumlah
    if debt.jumlah_terbayar >= debt.jumlah_total:
        debt.status = DebtStatus.lunas

    db.commit()
    db.refresh(debt)
    return debt


@router.delete("/{debt_id}", status_code=204)
def delete_debt(debt_id: int, db: Session = Depends(get_db)):
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Data hutang/piutang tidak ditemukan")

    has_payment = db.query(Transaction).filter(Transaction.debt_id == debt_id).first()
    if has_payment:
        raise HTTPException(
            status_code=400,
            detail="Tidak bisa dihapus karena sudah ada riwayat pembayaran terkait",
        )

    db.delete(debt)
    db.commit()