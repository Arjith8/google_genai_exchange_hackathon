from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.models import Base


def create_db_session() -> Session:
    engine = create_engine('sqlite:///database/test.db', echo=True)
    Base.metadata.create_all(engine)
    db_session = Session(engine)
    return db_session
    pass
