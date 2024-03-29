from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class Item(BaseModel):
    name: str
    quantity: int
    description: str = None

def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def startup():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            quantity INTEGER, 
            description TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            quantity INTEGER, 
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.get("/items/")
async def read_items():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = [dict(item) for item in c.fetchall()]
    conn.close()
    return items

@app.get("/products/")
async def read_products():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products = [dict(item) for item in c.fetchall()]
    conn.close()
    return products

@app.post("/items/")
async def create_item(item: Item):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO items (name, quantity, description) VALUES (?, ?, ?)', 
              (item.name, item.quantity, item.description))
    conn.commit()
    new_id = c.lastrowid  # Get the auto-generated ID of the newly created item
    conn.close()
    return {"id": new_id, "name": item.name, "quantity": item.quantity, "description": item.description}

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE items SET name = ?, quantity = ?, description = ? WHERE id = ?', 
              (item.name, item.quantity, item.description, item_id))
    conn.commit()
    conn.close()
    return {"id": item_id, "name": item.name, "quantity": item.quantity, "description": item.description}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return {"message": "Item deleted"}


#// Run the server
# cd backend
# sudo uvicorn main:app --reload --port 80
# http://localhost
#
# Access the API documentation at http://localhost/docs
#
#// Or Build & Run Docker Image
# docker build -t warehouse-service .
# docker run -d --name Store_1 -p 8000:8000 warehouse-service