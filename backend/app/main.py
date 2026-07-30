from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import accounts, categories, transactions, budgets, savings_goals, debts

app = FastAPI(title="Personal Finance App", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(savings_goals.router)
app.include_router(debts.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Finance App API jalan"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
