from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetOut, BudgetWithRealisasi

router = APIRouter(prefix="/budgets", tags=["Budgets"])


def _hitung_realisasi(db: Session, category_id: int, bulan: int, tahun: int) -> Decimal:
    total = (
        db.query(func.coalesce(func.sum(Transaction.jumlah), 0))
        .filter(
            Transaction.category_id == category_id,
            Transaction.tipe == TransactionType.expense,
            func.month(Transaction.tanggal) == bulan,
            func.year(Transaction.tanggal) == tahun,
        )
        .scalar()
    )
    return total


def _to_with_realisasi(db: Session, budget: Budget) -> BudgetWithRealisasi:
    realisasi = _hitung_realisasi(db, budget.category_id, budget.bulan, budget.tahun)
    sisa = budget.jumlah_budget - realisasi
    persentase = float(realisasi / budget.jumlah_budget * 100) if budget.jumlah_budget else 0.0
    return BudgetWithRealisasi(
        **BudgetOut.model_validate(budget).model_dump(),
        realisasi=realisasi,
        sisa=sisa,
        persentase=round(persentase, 1),
    )


@router.get("", response_model=List[BudgetWithRealisasi])
def list_budgets(
    db: Session = Depends(get_db),
    bulan: Optional[int] = None,
    tahun: Optional[int] = None,
):
    q = db.query(Budget)
    if bulan:
        q = q.filter(Budget.bulan == bulan)
    if tahun:
        q = q.filter(Budget.tahun == tahun)
    return [_to_with_realisasi(db, b) for b in q.all()]


@router.get("/{budget_id}", response_model=BudgetWithRealisasi)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget tidak ditemukan")
    return _to_with_realisasi(db, budget)


@router.post("", response_model=BudgetOut, status_code=201)
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="category_id tidak valid")
    if category.tipe.value != "expense":
        raise HTTPException(status_code=400, detail="Budget hanya berlaku untuk kategori expense")

    budget = Budget(**payload.model_dump())
    db.add(budget)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Budget untuk kategori ini di bulan/tahun tersebut sudah ada",
        )
    db.refresh(budget)
    return budget


@router.put("/{budget_id}", response_model=BudgetOut)
def update_budget(budget_id: int, payload: BudgetUpdate, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget tidak ditemukan")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return budget


@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget tidak ditemukan")
    db.delete(budget)
    db.commit()