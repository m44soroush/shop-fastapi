from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings


engine = create_engine(settings.SQLALCHEMY_URL,
                       connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine,
                            autocommit=False,
                            autoflush=False)

Base = declarative_base()
