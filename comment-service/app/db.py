import os
from sqlmodel import SQLModel, create_engine, Session

DB_DIR = "/app/data"
DB_PATH = f"{DB_DIR}/comment.db"

os.makedirs(DB_DIR, exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
