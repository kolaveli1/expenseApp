from fastapi import FastAPI, HTTPException
import os
import psycopg2
import urllib.parse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Hent DATABASE_URL fra environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL er ikke sat! Tjek Railway Variables.")

# Parse DATABASE_URL korrekt
parsed_url = urllib.parse.urlparse(DATABASE_URL)
dbname = parsed_url.path[1:]  # Fjern skråstregen foran db-navnet
user = parsed_url.username
password = parsed_url.password
host = parsed_url.hostname
port = parsed_url.port

# Funktion til at oprette en ny databaseforbindelse
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except psycopg2.OperationalError as e:
        print("❌ Databaseforbindelse fejlede:", e)
        raise HTTPException(status_code=500, detail="Databaseforbindelse fejlede")

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
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO expenses (name, price, date, category_id) VALUES (%s, %s, %s, %s) RETURNING id;",
        (expense.name, expense.price, expense.date, expense.category_id)
    )
    conn.commit()
    
    cur.close()
    conn.close()
    return {"message": "Expense added!"}

# Endpoint: Hent alle expenses
@app.get("/expenses/")
def get_expenses():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT expenses.id, expenses.name, expenses.price, expenses.date, categories.name as category 
        FROM expenses 
        JOIN categories ON expenses.category_id = categories.id
    """)
    expenses = cur.fetchall()

    cur.close()
    conn.close()

    return {"expenses": [{"id": e[0], "name": e[1], "price": e[2], "date": e[3], "category": e[4]} for e in expenses]}

# Endpoint: Opret en kategori
@app.post("/categories/")
def create_category(category: Category):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id;", (category.name,))
    conn.commit()

    cur.close()
    conn.close()
    
    return {"message": "Category added!"}

# Endpoint: Hent alle kategorier
@app.get("/categories/")
def get_categories():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM categories;")
    categories = cur.fetchall()

    cur.close()
    conn.close()

    return {"categories": [{"id": c[0], "name": c[1]} for c in categories]}

# Endpoint: Slet en kategori
@app.delete("/categories/{category_id}")
def delete_category(category_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM categories WHERE id = %s;", (category_id,))
    conn.commit()

    cur.close()
    conn.close()

    return {"message": "Category deleted!"}
