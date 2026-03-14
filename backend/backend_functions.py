import inspect
from typing import Dict
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from backend.query_handler import get_user
import os, re

### Define helper functions ###

def get_caller_filename(depth:int=1)->Dict[str,str|None]:
    """Helper function to get filename and function name of function at given depth in Inspect Stack.
    Example: get_called_filename() called from Logger(), itself called from ABC(). 
    Depth of 1 returns 'LoggerFile' and 'Logger', Depth of 2 returns 'ABCFile' and 'ABC'.
    Returns a dictionary with keys 'caller_filename','caller_func_name' and 'message'"""
    # Determine the calling file name
    frame = inspect.currentframe()
    depth_track = 0
    # Find the deepest possible fn in the Inspect Stack, upto the given depth
    while depth_track!=depth and frame is not None:
        frame = frame.f_back # don't worry about frame being None, fallbacks handled after the while loop
        if frame is not None: 
            depth_track+=1
    # fallback to handle possibility of None (asserts wouldn't handle Nones, try..catch wouldn't satisfy PyRight)
    caller_filename = frame.f_code.co_filename if frame is not None else __file__
    caller_func_name = frame.f_code.co_name if frame is not None else None
    return_object={"caller_filename":None,"caller_func_name":None,"message":""}
    # Warn the user if given depth is not reached
    if depth_track != depth:
        return_object["message"] = f"\nInspect Stack does not extend to depth:{depth}, deepest found caller at depth:{depth_track}"
    else:
        return_object["caller_filename"] = caller_filename
        return_object["caller_func_name"] = caller_func_name
        return_object["message"] = "Successfully retrieved requested function"
    return return_object

def confirm_password(hash, password)->bool:
    """
    Wrapper function to ensure the password hash stored and received password match.
    Currently uses check_password_hash(hash,password) from werkzeug.
    check_password_hash compares final hashes in constant time and is thus protected from timing attacks.
    """
    return check_password_hash(hash,password)

def hash_passwords(password_passed:str)->str:
    """Wrapper to generate and return password hash.
    Currently uses scrypt with work factor of 600,000 from werkzeug for production.
    Uses PBKDF2 with work factor of only 1000 to test database bottlenecking"""
    if os.getenv('TESTING_MODE') == 'True':
        password_hashed = generate_password_hash(password_passed, method='pbkdf2:sha256:1000')
    else:
        # Production gets full security
        password_hashed = generate_password_hash(password_passed)
    return password_hashed

# check admin
def admin_check(session:Session, user_id:int):
    """
    Checks for existence of user and whether user is admin or not
    """
    user = get_user(session, id=user_id)
    if not user:
             return "No Admin"
    return "Yes" if user.is_admin else "No"

def validate_patterns_regex(pattern:str, value_str:str)->bool:
    """Wrapper fn to match a value_str to the provided Regex pattern. 
    re.fullmatch() used to match entire string.
    Function is not protected against timing attakcs, do NOT use it for secret validation or password hash comparison.
    Use hmac digest comparison instead
    """
    return True if re.fullmatch(pattern,value_str) else False

def database_close(engine:Engine):
    """
    Closes all connections in the pool and merges 
    SQLite WAL files to the main database.
    """
    if engine:engine.dispose()