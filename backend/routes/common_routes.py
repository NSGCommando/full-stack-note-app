from flask import jsonify, Blueprint
import logging
from flask_jwt_extended import get_jwt, create_access_token, jwt_required, set_access_cookies, get_jwt_identity, unset_access_cookies
import backend.utils.backend_functions as bf, backend.database.queries.query_handler as qh, backend.utils.backend_constants as bc
from backend.utils.project_logger import get_project_logger
from backend.utils.blacklist_provider import get_jwt_blacklist

all_router = Blueprint('CommonRouter', __name__)

# get the global jwt blacklist
jwt_blacklist = get_jwt_blacklist()

# extract strings for regex patterns
user_pattern = bc.RegexPatterns.USERNAME_PATTERN.value
password_pattern = bc.RegexPatterns.PASSWORD_PATTERN.value

# set up logging
logger= get_project_logger(level=logging.INFO)

# route: DEV: flask homepage
@all_router.route("/")
def index():
    # Just to check Flask API works. Remove after dev is done, reuse the SQL command for admin dashboard (later)
    logger.info("Flask App running")
    return "flask API running"

# route: ALL: login, received from fetch URL in LoginPage
@all_router.route("/login",methods=["POST"])
@qh.data_conn
def login(data,session):
    username = data.get("username")
    login_password = data.get("password")
    user = qh.get_user(session, username=username)
    if not user:
        return jsonify({"error":"invalid credentials, user not found"}), 401 # 401 means unauthorized (Authentication failed or missing)

    if not bf.confirm_password(user.password, login_password):
        return jsonify({"error":"invalid credentials, password wrong"}), 401
    
    access_token = create_access_token(identity=str(user.id))
    response = jsonify({
        "message": "Login is successful",
        "username": username,
        "is_admin": user.is_admin
    })
    set_access_cookies(response, access_token)
    return response, 200

# route: ALL: logout and disable cookie
@all_router.route("/logout",methods=["GET"])
@jwt_required()
def logout_user():
    jwt_data = get_jwt()
    jti = jwt_data.get("jti")
    expiry = jwt_data.get("exp")
    if not isinstance(jti, str) or not isinstance(expiry, (int, float)):
        return jsonify({"message": "Invalid token payload, logout failed"}), 400
    jwt_blacklist.add_jti(jti,expiry)
    response = jsonify({"message":"Logout successful"})
    unset_access_cookies(response)
    return response,200

# route: ALL: verify current user token validity and return username, admin status if valid
@all_router.route("/verify_token", methods=['GET'])
@jwt_required()
@qh.data_conn
def verify(session,**kwargs):
    # If the code gets here, the token is valid
    current_user_id = get_jwt_identity()
    user = qh.get_user(session,id=current_user_id)
    if not user:
        return jsonify({"error":"invalid credentials, user not found"}), 401
    return {"message": "Token is valid", "username": user.user_name, "is_admin": user.is_admin}, 200

# route: ALL: signup username check
@all_router.route("/check_username",methods=["POST"])
@qh.data_conn
def check_username_taken(data, session):
    username = data.get("username")
    if username == "":
        return jsonify({"error":"Username failed validation, empty"}), 400
    # backend validation for username pattern restrictions
    if bf.validate_patterns_regex(user_pattern,username) is False:
        return jsonify({"error":"Username failed validation"}), 400
    user = qh.get_user(session, username=username)
    if not user:
        return jsonify({"message":"user doesn't exist"}), 200 # status ok
    else:
        return jsonify({"message":"unable to create user", "error":"user exists conflict"}), 409 # status conflict

# route: ALL: new user signup, only gets here AFTER username availability has been checked
@all_router.route("/signup",methods=["POST"])
@qh.data_conn
def signup_user(data, session):
    username = data.get("username")
    if username == "":
        return jsonify({"error":"Username failed validation, empty"}), 400
    password = data.get("password")
    if password == "":
        return jsonify({"error":"Password failed validation, empty"}), 400
    # backend validation for pattern restrictions
    if bf.validate_patterns_regex(user_pattern,username) is False:
        return jsonify({"error":"Username failed validation"}), 400
    if bf.validate_patterns_regex(password_pattern,password) is False:
        return jsonify({"error":"Password failed validation"}), 400
    password_hashed=bf.hash_passwords(password)
    try:
        qh.enter_data(session,username,password_hashed)
        session.commit()
        return jsonify({"message":"user signed up"}), 201 # request successfully created new user resource
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500