import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, render_template
from werkzeug.exceptions import HTTPException
from .config import Config
from .extensions import db, jwt, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from .auth.routes import auth_bp
    from .scan.routes import scan_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(scan_bp, url_prefix='/scan')

    # 全局异常处理
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({"msg": e.description, "code": e.code}), e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        app.logger.error(f"Unhandled exception: {e}")
        return jsonify({"msg": "Internal server error"}), 500

    @app.route('/')
    def index():
        return render_template('index.html')

    # 日志配置
    if not app.debug:
        os.makedirs('logs', exist_ok=True)
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

    return app