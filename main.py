from fastapi import FastAPI, HTTPException
import os
import psycopg2
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Expense Model
class Expense(BaseModel):
    name: str
    price: float
    date: datetime = datetime.now()
    category_id: int

# Category Model
class Category(BaseModel):
    name: str

# Endpoint: Opret en expense
@app.post("/expenses/")
def create_expense(expense: Expense):
    cur.execute(
        "INSERT INTO expenses (name, price, date, category_id) VALUES (%s, %s, %s, %s) RETURNING id;",
        (expense.name, expense.price, expense.date, expense.category_id)
    )
    conn.commit()
    return {"message": "Expense added!"}

# Endpoint: Hent alle expenses
@app.get("/expenses/")
def get_expenses():
    cur.execute("""
        SELECT expenses.id, expenses.name, expenses.price, expenses.date, categories.name as category 
        FROM expenses 
        JOIN categories ON expenses.category_id = categories.id
    """)
    expenses = cur.fetchall()
    return {"expenses": [{"id": e[0], "name": e[1], "price": e[2], "date": e[3], "category": e[4]} for e in expenses]}

# Endpoint: Opret en kategori
@app.post("/categories/")
def create_category(category: Category):
    cur.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id;", (category.name,))
    conn.commit()
    return {"message": "Category added!"}

# Endpoint: Hent alle kategorier
@app.get("/categories/")
def get_categories():
    cur.execute("SELECT id, name FROM categories;")
    categories = cur.fetchall()
    return {"categories": [{"id": c[0], "name": c[1]} for c in categories]}

# Endpoint: Slet en kategori
@app.delete("/categories/{category_id}")
def delete_category(category_id: int):
    cur.execute("DELETE FROM categories WHERE id = %s;", (category_id,))
    conn.commit()
    return {"message": "Category deleted!"}
