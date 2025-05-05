import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from src import crud, models

app = FastAPI()

# SQLite Database Setup
DATABASE = "items.db"

# Create the table if it doesn't exist
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            tax REAL
        )
        """)
        conn.commit()

# Initialize database (create table if not exists)
init_db()

# Pydantic model for the items
class Item(BaseModel):
    name: str
    description: str
    price: float
    tax: float | None = None

# Helper functions to interact with the SQLite database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/items/", response_model=List[Item])
def get_items():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    return [Item(**row) for row in rows]

@app.post("/items/", response_model=Item)
def create_item(item: Item):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, description, price, tax) VALUES (?, ?, ?, ?)",
                   (item.name, item.description, item.price, item.tax))
    conn.commit()
    item_id = cursor.lastrowid
    return {**item.dict(), "id": item_id}

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(**row)

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET name = ?, description = ?, price = ?, tax = ? WHERE id = ?",
                   (item.name, item.description, item.price, item.tax, item_id))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {**item.dict(), "id": item_id}

@app.delete("/items/{item_id}", response_model=Item)
def delete_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    return Item(**row)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI app!"}