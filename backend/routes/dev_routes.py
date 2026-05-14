from flask import Blueprint, abort, jsonify
import os
from backend.database.database_init import initialize_database
from backend.database.queries.query_handler import shutdown_sessions
from backend.utils.project_logger import get_project_logger
dev_route_logger= get_project_logger(module_name=__name__)

dev_router = Blueprint('DevRouter', __name__, url_prefix='/dev')

@dev_router.route("/test/reset-db",methods=["POST"])
def reset_db():
    if os.getenv("TESTING_MODE") != "True":
        abort(403)
    initialize_database(test_mode=True)
    dev_route_logger.info("Test database successfully reset")
    return jsonify({"message":"reset successful"}), 200

@dev_router.route("/test/shutdown-db",methods=["POST"])
def shutdown_db():
    if os.getenv("TESTING_MODE") != "True":
        abort(403)
    shutdown_sessions()
    dev_route_logger.info("Test database successfully shutdown")
    return jsonify({"message":"shutdown successful"}), 200