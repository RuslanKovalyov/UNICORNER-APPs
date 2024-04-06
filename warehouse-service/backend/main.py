from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class Item(BaseModel):
    name: str
    quantity: int
    description: str = None

class Product(BaseModel):
    name: str
    quantity: int
    description: str = None
    
class Recipe(BaseModel):
    name: str
    product_id: int
    product_name: str
    product_quantity: float  # Corrected from product_quantity to product_quantity
    product_metric: str # e.g. kg, g, l, ml, etc.
    items: str

    

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
    c.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            product_id INTEGER,
            product_name TEXT,
            product_quantity FLOAT,
            product_metric TEXT,
            items TEXT
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
    products = [dict(product) for product in c.fetchall()]
    conn.close()
    return products

@app.get("/recipes/")
async def read_recipes():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM recipes')
    recipes = [dict(recipe) for recipe in c.fetchall()]
    conn.close()
    return recipes

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

@app.post("/products/")
async def create_product(product: Product):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO products (name, quantity, description) VALUES (?, ?, ?)', 
              (product.name, product.quantity, product.description))
    conn.commit()
    new_id = c.lastrowid  # Get the auto-generated ID of the newly created product
    conn.close()
    return {"id": new_id, "name": product.name, "quantity": product.quantity, "description": product.description}

@app.post("/recipes/")
async def create_recipe(recipe: Recipe):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO recipes (name, product_id, product_name, product_quantity, product_metric, items) VALUES (?, ?, ?, ?, ?, ?)', 
            (recipe.name, recipe.product_id, recipe.product_name, recipe.product_quantity, recipe.product_metric, recipe.items))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return {"id": new_id, "name": recipe.name, "product_id": recipe.product_id, "product_name": recipe.product_name, "product_quantity": recipe.product_quantity, "product_metric": recipe.product_metric, "items": recipe.items}

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE items SET name = ?, quantity = ?, description = ? WHERE id = ?', 
              (item.name, item.quantity, item.description, item_id))
    conn.commit()
    conn.close()
    return {"id": item_id, "name": item.name, "quantity": item.quantity, "description": item.description}

@app.put("/products/{product_id}")
async def update_product(product_id: int, product: Product):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE products SET name = ?, quantity = ?, description = ? WHERE id = ?', 
              (product.name, product.quantity, product.description, product_id))
    conn.commit()
    conn.close()
    return {"id": product_id, "name": product.name, "quantity": product.quantity, "description": product.description}

@app.put("/recipes/{recipe_id}")
async def update_recipe(recipe_id: int, recipe: Recipe):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE recipes SET name = ?, product_id = ?, product_name = ?, product_quantity = ?, product_metric = ?, items = ? WHERE id = ?', 
              (recipe.name, recipe.product_id, recipe.product_name, recipe.product_quantity, recipe.product_metric, recipe.items, recipe_id))
    conn.commit()
    conn.close()
    return {"id": recipe_id, "name": recipe.name, "product_id": recipe.product_id, "product_name": recipe.product_name, "product_quantity": recipe.product_quantity, "product_metric": recipe.product_metric, "items": recipe.items}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return {"message": "Item deleted"}

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    return {"message": "Product deleted"}

@app.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
    conn.commit()
    conn.close()
    return {"message": "Recipe deleted"}

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