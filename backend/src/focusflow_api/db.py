from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from focusflow_api.config import get_settings

engine = create_engine(get_settings().database_url)


SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    pass
