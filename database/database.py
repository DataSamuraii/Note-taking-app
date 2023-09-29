import os
from dotenv import load_dotenv

from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

mysql_url = os.getenv("DB_URL")
engine = create_engine(mysql_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("MySQL connection established")
