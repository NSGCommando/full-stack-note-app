import os
from sqlalchemy import Engine
from backend.database_connect import get_session_factory, UserBase
from backend.table_class import UserData
from backend.backend_functions import hash_passwords
from backend.backend_constants import BackendPaths
from dotenv import load_dotenv
from backend.project_logger import get_project_logger

logger=get_project_logger()

load_dotenv()

def database_close(engine:Engine):
    """
    Closes all connections in the pool and merges 
    SQLite WAL files to the main database.
    """
    if engine:engine.dispose()
    logger.info("Successfully disposed all session engines")

def initialize_database(test_mode=False):
    """
    Create a new database at the selected path, default path is prod database
    Switch to test database by passing "test_mode" argument as True
    """
    if test_mode==True:
        path = BackendPaths.TEST_DATABASE_PATH.value
    else: path = BackendPaths.DATABASE_PATH.value
    session_factory = get_session_factory(path)
    engine = session_factory.bind
    # guarantee that engine is Engine object
    if not isinstance(engine, Engine):
        logger.error(f"Engine initialization failed for {path}")
        raise RuntimeError(f"Engine initialization failed for {path}")
    if test_mode: # clear data if in testing mode
        UserBase.metadata.drop_all(bind=engine)
    UserBase.metadata.create_all(bind=engine)
    # admin data
    password_hash = hash_passwords(os.getenv('ADMIN_KEY'))
    admin_name = os.getenv('ADMIN_USERNAME')
    with session_factory() as session:
        existing_admin = session.query(UserData).filter_by(user_name=admin_name).first()
        if not existing_admin:
            new_admin = UserData(
                user_name=admin_name,
                password=password_hash,
                is_admin=True
            )
            session.add(new_admin)
            session.commit()
    database_close(engine)

if __name__ == "__main__":
    initialize_database()    