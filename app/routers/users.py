from fastapi import APIRouter, Depends, HTTPException
from app.crud import crud
from app.schemas import user as userschemas
from app.schemas import item as itemschemas
from app.models import models
from app.db.database import SessionLocal, engine
from typing import List, Union

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=userschemas.User)
def create_user(user: userschemas.UserCreate, db=Depends(get_db)):
    db_user = crud.read_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400,
                            detail="Email already registered")
    return crud.create_user(db, user)


@router.get("/", response_model=List[userschemas.User])
def get_users(db=Depends(get_db)):
    users = crud.read_users(db)
    return users


@router.get("/{user_id}", response_model=userschemas.User)
def get_user(user_id: int, db=Depends(get_db)):
    user = crud.read_user(db, user_id)
    if not user:
        raise HTTPException(404, detail="Invalid ID")
    return user


@router.post("/{user_id}/items/", response_model=itemschemas.Item)
def add_user_item(user_id: int,
                  item: itemschemas.ItemCreate,
                  db=Depends(get_db)):
    item = crud.create_user_item(db, item, user_id)
    return item


@router.get("/{user_id}/items/",
            response_model=List[Union[itemschemas.Item, None]])
def get_user_items(user_id: int, db=Depends(get_db)):
    items = crud.read_user_items(db, user_id)
    return items


@router.get("/{user_id}/items/{item_id}", response_model=itemschemas.Item)
def get_user_item(user_id: int, item_id: int, db=Depends(get_db)):
    item = crud.read_user_item(db, user_id, item_id)
    return item
