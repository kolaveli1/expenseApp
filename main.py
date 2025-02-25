from fastapi import FastAPI
import os
import psycopg2

app = FastAPI()

# Hent DATABASE_URL fra Railway
DATABASE_URL = os.getenv("postgresql://postgres:FtxdzKtnlPplyxwBjhEResNPFZxIBWdi@postgres.railway.internal:5432/railway")

# Opret forbindelse til PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.get("/")
def home():
    return {"message": "Expense Tracker API is running!"}

@app.get("/expenses")
def get_expenses():
    cur.execute("SELECT * FROM expenses")
    expenses = cur.fetchall()
    return {"expenses": expenses}
