from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from focusflow_api.config import get_settings

engine = create_engine(get_settings().database_url)


class Base(DeclarativeBase):
    pass
