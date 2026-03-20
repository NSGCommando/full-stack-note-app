import os
from typing import Optional, Any, Tuple
from functools import wraps
from flask import request, jsonify
from sqlalchemy import Engine
from sqlalchemy.orm import Session, scoped_session
from backend.database.models.table_class import UserData, UserNotes
from backend.schemas.response_serializer import UserNotesView, UserView
from backend.database.database_connect import get_session_factory
from backend.utils.backend_constants import BackendPaths, CustomHeaders
# extract strings from constants file
db_path = BackendPaths.DATABASE_PATH.value
test_path = BackendPaths.TEST_DATABASE_PATH.value
frontend_header = CustomHeaders.CUSTOM_HEADER_FRONTEND.value
frontend_header_response = CustomHeaders.CUSTOM_HEADER_FRONTEND_RESPONSE.value

# persistent store for cached sessions by database path
_sessionPaths:dict[str, scoped_session[Session]] = {}

def shutdown_sessions():
    """Wrapper fn to call .dispose() on all cached session engines"""
    for session in _sessionPaths.values():
        engine = session.bind
        if not isinstance(engine, Engine):
            raise RuntimeError(f"Engine acquisition failed while trying to dispose engines during session shutdown")
        if engine:
            engine.dispose()
        session.remove()

def remove_cached_sessions():
    """Wrapper fn to call .remove() on all cached sessions"""
    for session in _sessionPaths.values():
        session.remove()

def get_cached_factory(path):
    """
    Check if a session for the given database path is cached or not
    Return it if yes, else create and cache a new session and then return it
    """
    if path not in _sessionPaths:
        _sessionPaths[path] = get_session_factory(path)
    return _sessionPaths[path]

def get_user(session:Session, **kwargs)->Optional[UserData]:
    """
    Helper function to find a specific user in database, either by id or username (returns first found user)
    Returns either None or an UserData object (defined in table_class.py)
    """
    user_id = kwargs.get("id")
    username = kwargs.get("username")
    if user_id:
        return session.get(UserData, user_id)
    elif username:
        return session.query(UserData).filter_by(user_name=username).first()
    return None

# enter new user data
def enter_data(session:Session, name:str, password_hash:str)->None:
    """
    Enter data for users
    Users cannot be admin via this input
    arguments: database_connection, username, password_hash
    """
    new_user = UserData(
                user_name=name,
                password=password_hash,
                is_admin=False
            )
    session.add(new_user)

# delete user data
def del_user(session:Session, id:int)->Optional[int]:
    """
    Delete data of users
    Commit and closure handled by calling fn
    """
    user = session.get(UserData, id)
    if not user:
        return None
    admin_status = user.is_admin if user else None
    if admin_status is True or admin_status is None: # cannot delete if user is admin OR doesn't exist
        return False
    else:
        session.delete(user)
        return True

# print entire user table
def print_db(session:Session)->list[dict[str, Any]]:
    """
    Function to return all data in the User Table
    Database location sent along with 'session' object
    calling function owns the connector and it's closure
    """
    # retrieve all results
    user_list = session.query(UserData.id,UserData.user_name,UserData.is_admin).all()
    return [UserView.to_dict(user) for user in user_list] # convert objects into list of dictionaries

# enter new note
def enter_note(session:Session,note:str,user_id:int,timestamp:str)->None:
    """
    Enter new user note into "user_notes" Table.
    Calling function owns commit and closure
    """
    new_note = UserNotes(
        user_id = user_id,
        note = note,
        timestamp = timestamp
        )
    session.add(new_note)

# return owner of a note
def del_note_user(session:Session,user_id:int,note_id:int):
    """
    Delete a particular note, given the note's user_id matches the calling user_id.
    Calling function owns commit and closure
    """
    note = session.get(UserNotes, note_id)
    if not note:return None
    if int(note.user_id)!=user_id: # only delete if the note belongs to the user
        return False
    else:
        session.delete(note)
        return True

# return all notes for one user
def view_user_notes(session:Session,user_id:int)->list[dict[str, Any]]:
    """
    Returns a list of notes for one user_id.
    Each dictionary object is of the form:
    # {'id': 1, 'note': 'My first note', 'timestamp': '2026-03-06T19:15:12+00:00'}
    """
    user_notes = session.query(UserNotes.id,UserNotes.note,UserNotes.timestamp).filter(UserNotes.user_id==user_id).order_by(UserNotes.id.desc()).all()
    return [UserNotesView.to_dict(note) for note in user_notes]

# decorator for boilerplate session creation and data check
def data_conn(f):
    """
    Decorator to confirm data validity, return data and connection objects.
    DB connection opened and closed by decorated function
    """
    @wraps(f)
    def edited_f(*args,**kwargs):
        data = request.get_json(silent=True) # silent ensures that data can be None
        # GET requests don't need a body, everyone else DOES, as per frontend schema
        # "if not data" will catch data being "None", "{}" or "[]" (they are all falsy values in Python)
        # "if data is None" only catches "None" identity, not falsy values
        if not data and request.method in ["POST","PUT", "DELETE"]:
            return jsonify({"error": "Invalid JSON"}), 400 # using decorator ensures I don't have to raise the error higher
        if data and request.method == "GET":
            return jsonify({"error":"Invalid GET Request"}), 400
        # now that the request type is confirmed to be semantically valid, continue
        
        if request.headers.get(frontend_header) != frontend_header_response:
            return jsonify({"error": "Unauthorised Access"}), 403 # reject the request if the custom header value is wrong
        
        # test path management
        if os.getenv('TESTING_MODE') == 'True':
            path=test_path # ensure testing path is included
        else:
            path=db_path
        
        sessionFactory = get_cached_factory(path)
        # So this is a context manager:
        # 'with' tells python this has standard __enter__ and __exit__ actions, on entering and leaving the block
        with sessionFactory() as session:
            try:
                return f(data=data, session=session, *args,**kwargs) # call original fn for object injection here
            except Exception as e:
                session.rollback()
                raise e
            # session.close() called automatically after "with" block is exited
    return edited_f