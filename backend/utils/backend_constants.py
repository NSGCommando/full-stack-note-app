# file paths, using Enum as super to enforce immutability, prevents overwriting
from enum import Enum
from pathlib import Path

class BackendPaths(Enum):
    """
    Class to store all path constants related to Backend
    """
    DATABASE_PATH = (Path(__file__).resolve().parents[1]/"data"/"database.db").as_posix() # save the database path
    TEST_DATABASE_PATH = (Path(__file__).resolve().parents[1]/"data"/"test_db.db").as_posix() # save the database path # save the test database file

class CustomHeaders(Enum):
    """
    Class to store all custom headers/custom tags
    Must match with the frontend constants
    """
    CUSTOM_HEADER_FRONTEND="R-Application-Service"
    CUSTOM_HEADER_FRONTEND_RESPONSE="Frontend-Service-R"

class RegexPatterns(Enum):
    """
    Class to store regex patterns used for username/password validation
    """
    USERNAME_PATTERN=r"[a-zA-Z0-9]{5,10}"
    PASSWORD_PATTERN=r"\S{8,20}"