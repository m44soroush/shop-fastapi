from pydantic import BaseModel, Field, EmailStr
from typing import List
from .item import Item


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1)
    age: int = Field(..., lt=120, ge=0)


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    items: List[Item] = []

    class Config:
        orm_mode = True
