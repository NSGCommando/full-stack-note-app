import os
from sqlalchemy import Engine
from pathlib import Path
from backend.database.database_connect import get_session_factory, UserBase
from backend.database.models.table_class import UserData
from backend.utils.backend_functions import hash_passwords, database_close
from backend.utils.backend_constants import BackendPaths
from dotenv import load_dotenv
from backend.utils.project_logger import get_project_logger

logger=get_project_logger()

load_dotenv()

def seed_admin(session_factory):
    """Helper function to seed an admin account into database"""
    # admin data
    secret_key = os.getenv('ADMIN_KEY')
    assert secret_key is not None
    password_hash = hash_passwords(secret_key)
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

def initialize_database(test_mode=False):
    """
    Create a new database at the selected path, default path is prod database.
    Switch to test database by passing "test_mode" argument as True
    """
    data_dir = Path(__file__).resolve().parents[1]/"data"
    data_dir.mkdir(parents=True,exist_ok=True)
    if test_mode==True:
        path = BackendPaths.TEST_DATABASE_PATH.value
    else: path = BackendPaths.DATABASE_PATH.value
    db_present = Path(path).exists()
    print(db_present, path)
    session_factory = get_session_factory(path)
    engine = session_factory.bind
    # guarantee that engine is Engine object
    if not isinstance(engine, Engine):
        logger.error(f"Engine initialization failed for {path}")
        raise RuntimeError(f"Engine initialization failed for {path}")
    if test_mode: # clear data if in testing mode
        UserBase.metadata.drop_all(bind=engine)
        UserBase.metadata.create_all(bind=engine)
    elif db_present is False: # ONLY recreate the database if it doesn't exist already
        UserBase.metadata.create_all(bind=engine)
        logger.info(f"Database created at {path}")
    if db_present is False:
        seed_admin(session_factory)
    database_close(engine)

if __name__ == "__main__":
    initialize_database()