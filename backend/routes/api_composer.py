from flask import Blueprint
from backend.routes.admin_routes import admin_router 
from backend.routes.user_routes import user_router
from backend.routes.common_routes import all_router

api_composer = Blueprint('Api', __name__, url_prefix='/api')

# register route blueprints to the top-level blueprint
api_composer.register_blueprint(admin_router)
api_composer.register_blueprint(user_router)
api_composer.register_blueprint(all_router)