from sqlmodel import SQLModel, create_engine, Session


mysql_url = "mysql+pymysql://root:password@localhost/dbname"
engine = create_engine(mysql_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("MySQL connection established")
