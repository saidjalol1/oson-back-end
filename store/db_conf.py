from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config
import pytz

DATABASE_URL = config(
    "DATABASE_URL",
    default="postgresql+psycopg2://postgres:postgres@localhost:5432/oson_db",
)


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_time():
    tz = pytz.timezone('Asia/Tashkent')
    return datetime.now(tz)