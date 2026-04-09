from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_cors import CORS
import logging, os, sys, signal, backend.utils.backend_constants as bc, backend.database.queries.query_handler as qh
from backend.utils.project_logger import get_project_logger
from backend.routes.api_composer import api_composer
from backend.utils.blacklist_provider import get_jwt_blacklist

# get the global jwt blacklist
jwt_blacklist = get_jwt_blacklist()

# extract string for custom header
frontend_header = bc.CustomHeaders.CUSTOM_HEADER_FRONTEND.value
frontend_header_response = bc.CustomHeaders.CUSTOM_HEADER_FRONTEND_RESPONSE.value
application = Flask(__name__) # expose the app
# set up logging
if os.getenv("TESTING_MODE") == "True":
    app_logger= get_project_logger(logging.DEBUG)
    app_logger.warning("WARNING: USING TEST DATABASE")
else:
    app_logger= get_project_logger(logging.INFO)
    app_logger.info("INFO: USING PRODUCTION DATABASE")

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

# register top-level api blueprint to the application
application.register_blueprint(api_composer)

# route: APP: tearDown function after request, cannot move this into a route blueprint without an app factory (to use current_app)
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