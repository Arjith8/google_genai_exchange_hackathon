from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.models import Base


def create_db_session() -> Session:
    """
    Create and return DB session.
    """
    engine = create_engine("sqlite:///database/test.db", echo=True)
    Base.metadata.create_all(engine)
    return Session(engine)
