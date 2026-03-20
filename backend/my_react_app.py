from dotenv import load_dotenv
from datetime import datetime, timezone
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, get_jwt, create_access_token, jwt_required, set_access_cookies, get_jwt_identity, unset_access_cookies
from datetime import timedelta
from flask_cors import CORS
import logging, os, sys, signal, backend.utils.backend_functions as bf, backend.utils.backend_constants as bc, backend.database.queries.query_handler as qh
from backend.utils.project_logger import get_project_logger
from backend.utils.blacklist_cache import BlacklistCache
# Setup JWT blacklister and cleaner thread
jwt_blacklist = BlacklistCache()

# extract string for custom header
frontend_header = bc.CustomHeaders.CUSTOM_HEADER_FRONTEND.value
frontend_header_response = bc.CustomHeaders.CUSTOM_HEADER_FRONTEND_RESPONSE.value
# extract strings for regex patterns
user_pattern = bc.RegexPatterns.USERNAME_PATTERN.value
password_pattern = bc.RegexPatterns.PASSWORD_PATTERN.value
application = Flask(__name__) # expose the app
# set up logging
if os.getenv("TESTING_MODE") == "True":
    app_logger= get_project_logger(logging.DEBUG)
    app_logger.warning("WARNING: USING TEST DATABASE")
else:
    app_logger= get_project_logger(logging.INFO)
    application.logger.info("INFO: USING PRODUCTION DATABASE")

# allows the app to receive requests from the Vite server IP, and allow browser to attach cookies
CORS(application, supports_credentials=True,origins=["http://localhost:5173"], allow_headers=["Content-Type",frontend_header])

# Secret key for JWT signing
load_dotenv()
# set up application's configs for JWT manager
application.config["JWT_SECRET_KEY"] = os.getenv('SECRET_SIGN_KEY')
application.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10) # token expires after 10 minutes
application.config["JWT_TOKEN_LOCATION"] = ["cookies"]
application.config["JWT_COOKIE_SECURE"] = False # running on localhost, so no SSH
application.config["JWT_COOKIE_CSRF_PROTECT"] = False # Didn't setup CSRF double token security isn't implemented
application.config["JWT_COOKIE_SAMESITE"] = "Lax" # To prevent browser from attaching JWTs to forged requests
jwt = JWTManager(application) # create the JWT manager instance for the exposed application

# define the blacklist loader callback
@jwt.token_in_blocklist_loader
def check_jwt_revoked(jwt_header,jwt_data):
    """Callback function to check token in blacklist or not"""
    jti = jwt_data.get("jti")
    if jti is None: return False
    return jwt_blacklist.check_blacklist(jti)

# route: DEV: flask homepage
@application.route("/")
def index():
    # Just to check Flask API works. Remove after dev is done, reuse the SQL command for admin dashboard (later)
    app_logger.info("Flask App running")
    return "flask API running"

# route: ALL: login, received from fetch URL in LoginPage
@application.route("/api/login",methods=["POST"])
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
@application.route("/api/logout",methods=["GET"])
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
@application.route("/api/verify_token", methods=['GET'])
@jwt_required()
@qh.data_conn
def verify(session,**kwargs):
    # If the code gets here, the token is valid
    current_user_id = get_jwt_identity()
    user = qh.get_user(session,id=current_user_id)
    if not user:
        return jsonify({"error":"invalid credentials, user not found"}), 401
    return {"message": "Token is valid", "username": user.user_name, "is_admin": user.is_admin}, 200

# route: ADMIN: retrieve all users in database
@application.route("/api/show-users",methods=["GET"])
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
@application.route("/api/users-delete",methods=["DELETE"])
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

# route: ALL: signup username check
@application.route("/api/check_username",methods=["POST"])
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
@application.route("/api/signup",methods=["POST"])
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

# route: USER: Add new note
@application.route("/api/user-add-note",methods=["POST"])
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
@application.route("/api/notes-delete",methods=["DELETE"])
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
@application.route("/api/user-view-notes",methods=["GET"])
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

# route: ALL: tearDown function after request
@application.teardown_appcontext
def remove_session(exception=None):
    """
    Cleans up all scoped sessions created during the request.
    """
    # obtain the request cache from the query handler and wipe all factory sessions for this thread
    qh.remove_cached_sessions()

def handle_shutdowns(sig, frame):
    """A shutdown function to handle both dev SIGNIT and docker signals (SIGTERM, SIGQUIT)"""
    app_logger.info(f"[INFO] Shutdown signal {sig} received. Cleaning up...")
    qh.shutdown_sessions()
    app_logger.info("[INFO] Session shut down. Exiting.")
    sys.exit(0)

# catch the SIQUIT from Linux distros
signals_to_catch = ["SIGINT", "SIGTERM", "SIGQUIT"]
for sig_name in signals_to_catch:
    # Check if the current OS actually supports this signal
    if hasattr(signal, sig_name):
        sig_num = getattr(signal, sig_name)
        signal.signal(sig_num, handle_shutdowns)
        app_logger.info(f"[info] Registered handler for {sig_name}")
    else:
        # This will trigger on Windows for SIGQUIT, but stay silent in Docker
        app_logger.info(f"[info] {sig_name} not supported on this OS. Skipping.")

if __name__=="__main__":
    application.run(debug=True,host='0.0.0.0',use_reloader=False) # the reloader starts a second Flask process
    # This process causes issues if Docker tries to shutdown as the signal won't be passed to the App's process
    # and the reloader will hard shutdown the app