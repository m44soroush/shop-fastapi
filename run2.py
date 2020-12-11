from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

my_app = FastAPI()

db: dict = {}


class Item(BaseModel):
    id: Optional[int] = None
    name: str
    price: int
    color: Optional[str] = None


@my_app.get("/")
def get_root():
    return "This is root page!"


@my_app.get("/items/{item_id}")
def get_item(item_id: int):
    try:
        return db[item_id]
    except(KeyError):
        return "ID not found!"


@my_app.post("/items")
def add_item(item: Item):
    if not item.id:
        id = len(db) + 1
        item.id = id
    db.update({item.id: item})
    return {"message": "item added", "item": item}


@my_app.get("/items")
def get_itmes():
    if not db:
        return "database is empty"
    return db
