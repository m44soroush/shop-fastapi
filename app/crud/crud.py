from sqlalchemy.orm import Session
from pydantic import EmailStr
from app.models import models
from app.schemas import user as userschema
from app.schemas import item as itemschema
from app.core import security


def create_user(db: Session, user: userschema.UserCreate) -> models.User:
    hashed_password = security.get_hash_password(user.password)
    user = userschema.UserBase(**user.dict())
    db_user = models.User(**user.dict(), hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def read_users(db: Session) -> models.User:
    db_users = db.query(models.User).all()
    return db_users


def create_user_item(db: Session,
                     item: itemschema.ItemCreate,
                     owner_id: int) -> itemschema.Item:
    db_item = models.Item(**item.dict(), owner_id=owner_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def read_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    return db_user


def read_user_items(db: Session, user_id: int):
    db_items = db.query(models.Item).filter(
        models.Item.owner_id == user_id).all()
    return db_items


def read_user_by_email(db: Session, user_email: EmailStr):
    db_user = db.query(models.User).filter(
        models.User.email == user_email
    ).first()
    return db_user


def read_user_item(db: Session, user_id: int, item_id: int) -> models.Item:
    db_item = db.query(models.Item).filter(
        models.Item.id == item_id,
        models.Item.owner_id == user_id).first()
    return db_item
