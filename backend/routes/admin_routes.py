from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
import backend.utils.backend_functions as bf, backend.database.queries.query_handler as qh

admin_router = Blueprint('AdminRouter', __name__, url_prefix='/admin')

# route: ADMIN: retrieve all users in database
@admin_router.route("/show-users",methods=["GET"])
@jwt_required()
@qh.data_conn
def get_users(session,**kwargs):
    admin_id =  int(get_jwt_identity())
    admin_checked = bf.admin_check(session, admin_id)
    match admin_checked:
        case "No Admin":return jsonify({"error":"invalid credentials, user not found"}), 401
        case "No":return jsonify({"error":"invalid credentials, user is not Admin"}), 403
        case "Yes":
            user_list = qh.print_db(session)
            return jsonify({
                "users":user_list,
                "user_count":len(user_list),
                "message":"success fetching all users"
            }), 200

# route: ADMIN: delete an user
@admin_router.route("/users-delete",methods=["DELETE"])
@jwt_required()
@qh.data_conn
def delete_user(data, session):
    """
    Delete user by id
    Returns a json message and status code
    """
    target_user_id = data.get("target_id")
    admin_id = int(get_jwt_identity()) # ALWAYS cast values expected to be ints to int explicitly for type-safety
    admin_checked = bf.admin_check(session,admin_id)
    match admin_checked:
        case "No Admin":return jsonify({"error":"invalid credentials, user not found"}), 401
        case "No":return jsonify({"error":"invalid credentials, user is not Admin"}), 403
        case "Yes":
            action_result = qh.del_user(session,target_user_id)
            if not action_result:return jsonify({"error":"Target user cannot be deleted (admin or no user)"}), 403
            else:
                session.commit()
                return jsonify({"message":"deletion successful"}), 200