# =========================================================
# app/__init__.py
# Flask application factory
# =========================================================

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.config import Config

# Global extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ---------- Session cookie config ----------
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    # ---------- Extensions ----------
    db.init_app(app)
    migrate.init_app(app, db)

    # ---------- CORS ----------
    CORS(
        app,
        supports_credentials=True,
        origins=app.config.get('CORS_ORIGINS', [
            'http://localhost:5500',
            'http://127.0.0.1:5500',
        ]),
        allow_headers=['Content-Type'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    )

    # ---------- Ensure upload folder exists ----------
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ---------- Serve uploaded images ----------
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

       # ---------- Register blueprints ----------
    from app.routes.auth import auth_bp
    from app.routes.items import items_bp
    from app.routes.recognize import recognize_bp
    from app.routes.borrowings import borrowings_bp
    from app.routes.maintenance import maintenance_bp
    from app.routes.reports import reports_bp
    from app.routes.labs import labs_bp
    from app.routes.suppliers import suppliers_bp
    from app.routes.users import users_bp
    from app.routes.stock import stock_bp

    app.register_blueprint(auth_bp,        url_prefix='/api/auth')
    app.register_blueprint(items_bp,       url_prefix='/api/items')
    app.register_blueprint(recognize_bp,   url_prefix='/api')
    app.register_blueprint(borrowings_bp,  url_prefix='/api/borrowings')
    app.register_blueprint(maintenance_bp, url_prefix='/api/maintenance')
    app.register_blueprint(reports_bp,     url_prefix='/api/reports')
    app.register_blueprint(labs_bp,        url_prefix='/api/labs')
    app.register_blueprint(suppliers_bp,   url_prefix='/api/suppliers')
    app.register_blueprint(users_bp,       url_prefix='/api/users')
    app.register_blueprint(stock_bp,       url_prefix='/api/stock')

    # ---------- Health check ----------
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Lab Inventory API running'}

    return app