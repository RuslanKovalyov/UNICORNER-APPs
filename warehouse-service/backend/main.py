from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import json

sqlite3.connect('inventory.db')

class Item(BaseModel):
    id: int
    name: str
    quantity: int
    description: str = None

# create tables in the database
conn = sqlite3.connect('inventory.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER, description TEXT)')
conn.commit()
conn.close()

app = FastAPI()
# app = FastAPI(docs_url=None, redoc_url=None)

# mplement CRUD operations:

@app.get("/")
def read_root():
    return {"Hello": "Warehouse-Service"}

@app.get("/items/")
async def read_items():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = c.fetchall()
    conn.close()
    return json.loads(json.dumps({item[0]: {"id": item[0], "name": item[1], "quantity": item[2], "description": item[3]} for item in items}))

@app.post("/items/")
async def create_item(item: Item):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('INSERT INTO items (id, name, quantity, description) VALUES (?, ?, ?, ?)', (item.id, item.name, item.quantity, item.description))
    conn.commit()
    conn.close()
    return json.loads(json.dumps({"id": item.id, "name": item.name, "quantity": item.quantity, "description": item.description}))

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('UPDATE items SET name = ?, quantity = ?, description = ? WHERE id = ?', (item.name, item.quantity, item.description, item_id))
    conn.commit()
    conn.close()
    return json.loads(json.dumps({"id": item_id, "name": item.name, "quantity": item.quantity, "description": item.description}))

@app.put("/items/{item_id}/increase/{quantity}")
async def increase_quantity(item_id: int, quantity: int):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = c.fetchone()
    c.execute('UPDATE items SET quantity = ? WHERE id = ?', (item[2] + quantity, item_id))
    conn.commit()
    conn.close()
    return json.loads(json.dumps({"id": item[0], "name": item[1], "quantity": item[2] + quantity, "description": item[3]}))

@app.put("/items/{item_id}/subtract/{quantity}")
async def subtract_quantity(item_id: int, quantity: int):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = c.fetchone()
    c.execute('UPDATE items SET quantity = ? WHERE id = ?', (item[2] - quantity, item_id))
    conn.commit()
    conn.close()
    return json.loads(json.dumps({"id": item[0], "name": item[1], "quantity": item[2] - quantity, "description": item[3]}))

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    conn = sqlite3.connect('inventory.db')
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