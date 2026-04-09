from flask import jsonify, Blueprint
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required, get_jwt_identity
import backend.utils.backend_functions as bf, backend.database.queries.query_handler as qh

user_router = Blueprint('UserRouter', __name__, url_prefix='/user')

# route: USER: Add new note
@user_router.route("/add-note",methods=["POST"])
@jwt_required()
@qh.data_conn
def add_new_note(data, session):
    user_id=int(get_jwt_identity()) # ALWAYS cast values expected to be ints to int explicitly for type-safety
    timestamp = datetime.now(timezone.utc).isoformat()
    note=data.get("note")
    if note is None or note == "": # 'is' checks if the var is of type None, == checks if the string is "" (Identity vs Equality)
        return jsonify({"error":"Note cannot be empty"}), 400
    qh.enter_note(session,note,user_id,timestamp)
    session.commit()
    return jsonify({"message":"Success adding new note"}), 201

# route: USE: Delete note
@user_router.route("/notes-delete",methods=["DELETE"])
@jwt_required()
@qh.data_conn
def delete_note(data, session):
    user_id=int(get_jwt_identity())
    note_id = data.get("note_id")
    action_result = qh.del_note_user(session, user_id, note_id)
    if action_result is None: return jsonify({"error":f"Note {note_id} not found"}), 400
    elif action_result is False: return jsonify({"error":f"Note {note_id} does not belong to user {user_id}"}), 403
    else:
        session.commit()
        return jsonify({"message":"Note successfully deleted"}), 200

# route: USER: Show all user's notes
@user_router.route("/view-notes",methods=["GET"])
@jwt_required()
@qh.data_conn
def view_notes(session, **data):
    user_id=int(get_jwt_identity())
    # By default returns notes for specific user_id, so ownership check not needed again
    user_notes=qh.view_user_notes(session,user_id)
    # implement note fetching by user id
    return jsonify({
        "notes":user_notes,
        "message":"Success fetching all user notes"
    }), 200