from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.account import Account
from app.models.savings_goal import SavingsGoal
from app.schemas.savings_goal import (
    SavingsGoalCreate,
    SavingsGoalUpdate,
    SavingsGoalOut,
    SavingsGoalContribution,
)

router = APIRouter(prefix="/savings-goals", tags=["Savings Goals"])


@router.get("", response_model=List[SavingsGoalOut])
def list_savings_goals(db: Session = Depends(get_db)):
    return db.query(SavingsGoal).all()


@router.get("/{goal_id}", response_model=SavingsGoalOut)
def get_savings_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal tidak ditemukan")
    return goal


@router.post("", response_model=SavingsGoalOut, status_code=201)
def create_savings_goal(payload: SavingsGoalCreate, db: Session = Depends(get_db)):
    if payload.account_id:
        if not db.query(Account).filter(Account.id == payload.account_id).first():
            raise HTTPException(status_code=400, detail="account_id tidak valid")

    goal = SavingsGoal(**payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.put("/{goal_id}", response_model=SavingsGoalOut)
def update_savings_goal(goal_id: int, payload: SavingsGoalUpdate, db: Session = Depends(get_db)):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal tidak ditemukan")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


@router.post("/{goal_id}/contribute", response_model=SavingsGoalOut)
def contribute_to_goal(
    goal_id: int, payload: SavingsGoalContribution, db: Session = Depends(get_db)
):
    """Nambah current_jumlah goal. Tidak otomatis bikin transaksi/potong saldo akun
    karena goal ini sifatnya tracking target, bukan wallet terpisah."""
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal tidak ditemukan")
    if payload.jumlah <= 0:
        raise HTTPException(status_code=400, detail="Jumlah kontribusi harus lebih dari 0")

    goal.current_jumlah = goal.current_jumlah + payload.jumlah
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=204)
def delete_savings_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal tidak ditemukan")
    db.delete(goal)
    db.commit()