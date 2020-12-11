from pydantic import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_URL: str = "sqlite:///app/db/my_db.db"


settings = Settings()
