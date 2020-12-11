from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routers import users
import uvicorn
# import os
# import pathlib

# print("***************")
# print(pathlib.Path(__file__).parent.absolute())
# print(pathlib.Path().absolute())
# print(os.path.abspath(os.getcwd()))
tags_metadata = [
    {
        "name": "user",
        "description": "Manage users from database"
    }
]

app = FastAPI(
    title="My FastAPI Crud",
    description="This is my first API with FastAPI and SQLite",
    version="1.0.2",
    openapi_tags=tags_metadata,
    openapi_url="/api/v1/openapi.json"
)


app.include_router(users.router, prefix="/users", tags=["user"])


@ app.get("/")
async def get_root():
    contetnt = """
    <h1>This is the root page</h1>
    """
    return HTMLResponse(contetnt)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
