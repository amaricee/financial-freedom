from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut, CategoryTree

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/tree", response_model=List[CategoryTree])
def get_category_tree(db: Session = Depends(get_db)):
    """Kategori top-level (parent_id null) beserta children-nya, nested."""
    return db.query(Category).filter(Category.parent_id.is_(None)).all()


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    return category


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    if payload.parent_id:
        parent = db.query(Category).filter(Category.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="parent_id tidak valid")
        if parent.tipe != payload.tipe:
            raise HTTPException(
                status_code=400,
                detail="Tipe sub-kategori harus sama dengan tipe kategori induknya",
            )

    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")

    has_children = db.query(Category).filter(Category.parent_id == category_id).first()
    if has_children:
        raise HTTPException(
            status_code=400, detail="Kategori tidak bisa dihapus karena masih punya sub-kategori"
        )

    has_transaction = db.query(Transaction).filter(Transaction.category_id == category_id).first()
    if has_transaction:
        raise HTTPException(
            status_code=400,
            detail="Kategori tidak bisa dihapus karena masih dipakai transaksi",
        )

    db.delete(category)
    db.commit()
