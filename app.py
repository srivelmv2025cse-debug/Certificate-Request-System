import os
from flask import Flask, render_template
from config import Config
from database.db import close_db, init_db
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register teardown
    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    # Global Error Handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", message="Access denied.", code=403), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", message="Resource not found.", code=404), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", message="Internal server error.", code=500), 500

    return app

app = create_app()

if __name__ == "__main__":
    # Ensure database is initialized before starting
    if not os.path.exists(Config.DATABASE_PATH):
        init_db(Config.DATABASE_PATH)
    print(f"Starting Certificate Request System on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
