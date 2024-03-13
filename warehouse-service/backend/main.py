from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    quantity: int
    description: str = None

# Sample in-memory "database"
inventory = {}

app = FastAPI()

# mplement CRUD operations:

@app.get("/")
def read_root():
    return {"Hello": "Warehouse-Service"}

@app.get("/items/")
async def read_items():
    return inventory

@app.post("/items/")
async def create_item(item: Item):
    inventory[item.id] = item
    return item

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    inventory[item_id] = item
    return item

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    del inventory[item_id]
    return {"message": "Item deleted"}


#// Run the server
# cd backend
# uvicorn main:app --reload
# http://0.0.0.0:8000
#
# Access the API documentation at http://127.0.0.1:8000/docs.
#
#// Or Build & Run Docker Image
# docker build -t warehouse-service .
# docker run -d --name Store_1 -p 8000:8000 warehouse-service