from fastapi import FastAPI, HTTPException
import os
import psycopg2
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Opret forbindelse til PostgreSQL
DATABASE_URL = os.getenv("postgresql://postgres:FtxdzKtnlPplyxwBjhEResNPFZxIBWdi@postgres.railway.internal:5432/railway")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Expense Model
class Expense(BaseModel):
    name: str
    price: float
    date: datetime = datetime.now()
    category: str | None = None

# Opret en expense
@app.post("/expenses/")
def create_expense(expense: Expense):
    cur.execute(
        "INSERT INTO expenses (name, price, date, category) VALUES (%s, %s, %s, %s) RETURNING id;",
        (expense.name, expense.price, expense.date, expense.category)
    )
    conn.commit()
    return {"message": "Expense added!"}

# Hent alle expenses
@app.get("/expenses/")
def get_expenses():
    cur.execute("SELECT * FROM expenses;")
    expenses = cur.fetchall()
    return {"expenses": expenses}

# Slet en expense
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    cur.execute("DELETE FROM expenses WHERE id = %s;", (expense_id,))
    conn.commit()
    return {"message": "Expense deleted!"}
