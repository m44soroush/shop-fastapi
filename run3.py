from typing import Optional, List, Union, Dict
from pydantic import BaseModel, Field, AnyUrl
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Path, Body, Query, status, File, Form
from fastapi import UploadFile, HTTPException, Header, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import JWTError, jwt
import uvicorn
import time

# openssl rand -hex 32
SECRET_KEY = "950a48a21d84b990f06f818e3c8527e908bc0be12c773c51fa6d61cdf7206311"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_TIME = 15

app = FastAPI()
pwd_context = CryptContext(schemes="bcrypt", deprecated="auto")
oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")

db: dict = {100:
            {"name": "mohammad",
             "age": 24,
             "gender": "m",
             "image": {
                 "name": "Profile pic",
                 "url": ["http://127.0.0.1:8000",
                         "http://google.com"]
             },
             "hashed_passwd":
             "$2b$12$RFIQTwWv3BQf1Ha.95s7teHqxcd0GeQ9FNdyBjt5RSTPnm1jVpNbW",
             "user_id": 100
             }
            }


class Image(BaseModel):
    name: str
    url: List[AnyUrl] = []


class BaseUser(BaseModel):
    name: str
    age: int = Field(..., gt=0, lt=120)
    gender: Optional[str] = Field(None, max_length=1,
                                  description="""Insert m for male,
                                   f for female, o for others""")
    image: Optional[Image] = Field(None)


class UserIn(BaseUser):
    passwd: str

    class Config:
        schema_extra = {
            "example": {
                "name": "mohammad",
                "passwd": "11223344",
                "age": 24,
                "gender": "m",
                "image": {
                    "name": "Profile pic",
                    "url": ["http://127.0.0.1:8000",
                            "http://google.com"]
                }
            }
        }


class UserOut(BaseUser):
    user_id: int = Field(..., ge=100)

    class Config:
        schema_extra = {
            "example": {
                "name": "mohammad",
                "age": 24,
                "gender": "m",
                "image": {
                    "name": "Profile pic",
                    "url": ["http://127.0.0.1:8000",
                            "http://google.com"]
                }
            }
        }


class UserDB(UserOut):
    hashed_passwd: str


def hash_passwd(passwd: str):
    hashed_passwd = pwd_context.hash(passwd)
    return hashed_passwd


def verify_passwd(plain, hashed):
    verify = pwd_context.verify(plain, hashed)
    return verify


def authenticate_user(database, username, password) -> Union[UserOut, bool]:
    id = int(username)
    user = get_user_from_db(database, id)
    if not user:
        return False
    if not verify_passwd(password, user.hashed_passwd):
        return False
    user_out = UserOut(**user.dict())
    return user_out


def create_access_token(data: dict, expire_td: Optional[timedelta] = None):
    to_encode = data.copy()
    if expire_td:
        exp = datetime.utcnow() + expire_td
    else:
        exp = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": exp})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def save_to_db(database, user: UserIn):
    id = len(db) + 100
    hashed_passwd = hash_passwd(user.passwd)

    user_db = UserDB(user_id=id, hashed_passwd=hashed_passwd, **user.dict())

    database.update({user_db.user_id: user_db.dict()})
    print("********saved to database*************")
    return user_db


def get_user_from_db(database, id: int) -> UserDB:
    if id not in database.keys():
        return None
    return UserDB(**database[id])


def token_to_user(token: str) -> UserDB:
    print(token)
    id = int(token.split("tok")[1])
    user = get_user_from_db(id)
    return user


async def get_current_user(token=Depends(oath2_scheme)) -> UserOut:
    cre_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                  detail="Credential Error!!",
                                  headers={"WWWW-Authenticate": "Bearer"})
    time_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                   detail="Token expired!!")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get("user_id")
        exp = payload.get("exp")
    except(JWTError):
        raise cre_exception
    if datetime.fromtimestamp(exp) < datetime.utcnow():
        raise time_exception
    user = get_user_from_db(db, user_id)
    if user is None:
        raise cre_exception
    user_out = UserOut(**user.dict())
    return user_out


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/", tags=["files"])
def get_upload_page():
    content = """
<form action="/file/" enctype="multipart/form-data" method="post">
<input name="username" type="text" Username>
<input name="passwd" type="text" Password>
<input name="file" type="file" multiple>
<input name="upload" type="file" upload>
<input type="submit">
</form>
    """
    return HTMLResponse(content)


@app.post("/file/", tags=["files"])
async def create_file(file: UploadFile = File(...),
                      username: str = Form(...),
                      passwd: str = Form(...),
                      upload: UploadFile = File(...)):
    upload_content = await upload.read()
    await upload.close()
    with open('fast.png', 'wb') as png:
        png.write(upload_content)
    print(type(upload_content))
    return {
        "file_content": file.file.read(),  # reading without async
        "username": username,
        "password": passwd,
        "Upload File Name": upload.filename,
        "Upload File Type": upload.content_type
    }


@app.get("/item/{item}",
         status_code=222,
         response_model=UserOut,
         description="Get user information via query parameters",
         tags=["users"])
def get_user_by_query(
    item: str = Path(..., max_length=10,
                     description="Item",
                     example="user"),
    id: Optional[int] = Query(None, ge=100,
                              description="User ID",
                              example=100)):
    if item == "user":
        if id not in db.keys():
            raise HTTPException(status_code=404,
                                detail="Not found in the database!",
                                headers={"X-Error": "sth"})
    else:
        return {"message": "You didn't select any item!"}


@app.get("/user/me", response_model=UserOut, tags=["auth"])
async def read_user_me(current_user: UserOut = Depends(get_current_user)):
    return current_user


@app.get("/user/{user_id}", response_model=Union[UserOut, Dict],
         tags=["users"])
def get_user_by_id(user_id: int = Path(..., ge=100, example=150)):
    try:
        return db[user_id]
    except(KeyError):
        return {"message": "not found in the database"}


@app.post("/user",
          response_model=Dict[str, UserOut],
          status_code=status.HTTP_201_CREATED,
          tags=["users"])
def create_user(
    user: UserIn = Body(
        ...,
        example={
        "name": "mohammad",
        "passwd": "11223344",
        "age": 24,
        "gender": "m",
        "image": {
            "name": "Profile pic",
            "url": ["http://127.0.0.1:8000",
                    "http://google.com"]
        }},
        embed=True,
    ),
    creator: str = Body(...),
    my_header: Optional[str] = Header(None)
):
    user_db = save_to_db(db, user)
    return {"user": user_db}


@app.get("/db", response_model=Dict[int, UserDB],
         response_description="Database entry",
         tags=["users"]
         )
def get_db():
    """
    You can get database entries from this page:
    In the standard way you could not see the hashed password
    but here you can get ```UserDB``` model and see all the
     **important** information here
    """
    return db


@app.post("/token", tags=["auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        int(form_data.username)
    except(ValueError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Unprocessable data")

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")
    return {"access_token": create_access_token(
        {"user_id": user.user_id},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_TIME)),
        "token-type": "bearer"}


@app.get("/check-login", tags=["auth"])
async def check_auth(token=Depends(oath2_scheme)):
    return token

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
