from fastapi import FastAPI
from enum import Enum
from typing import Optional

app = FastAPI()


class DayName(str, Enum):
    sat = 'sat'
    sun = 'sun'
    mun = 'mon'
    tue = 'tue'
    wed = 'wed'
    thu = 'thu'
    fri = 'fri'


@app.get("/", summary="This is for root page")
def root_page():
    return "<h1>Hi Fast</h1>"


@app.get("/users/{owner}/cars/{brand}")
def get_imtes(owner: str, brand: str, price: int,
              mileage: Optional[int] = None):
    car = {"Owner": owner, "Cars": {"Car brand": brand, "Car price": price}}

    if mileage:
        car['Cars'].update({"Mileage": mileage})

    return car


@app.get("/users/me")
def get_users_me():
    return {"user": "myself!"}


@app.get("/users/{user_id}")
def get_users(user_id: int):
    return {"user_id": user_id}


@app.get("/tasks/{day_name}")
def get_day_name(day_name: DayName):
    return f"your selected day is: {day_name}"
