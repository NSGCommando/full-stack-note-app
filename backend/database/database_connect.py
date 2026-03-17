from typing import Dict, Any
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, scoped_session, sessionmaker
from pathlib import Path

class UserBase(DeclarativeBase): # All models will inherit from this
    def to_dict(self)->Dict[str,Any]:
            """
            Generic to_dict mthod to convert object into dictionary.
            Returns a dictionary of structure 'key':'value'
            """
            return {field.name: getattr(self, field.name) for field in self.__table__.columns}

def get_session_factory(db_path:str)->scoped_session[Session]:
    """
    Input argument: a filepath to the corresponding database.
    Returns a scoped sessionmaker instance tied to the specific path.
    """
    engine = create_engine(f"sqlite:///{Path(db_path).resolve().as_posix()}", connect_args={"timeout": 5})
    # Fn to set SQLite3 timeout and WAL mode setup
    # No need to return SQLite3 rows since SQLAlchemy works via class attrbutes and the User Model
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    return scoped_session(session_factory=sessionmaker(bind=engine)) # return a session factory scoped to request threads