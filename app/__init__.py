import os
from dotenv import load_dotenv

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_bcrypt import Bcrypt

# Cargar variables de entorno desde .env
load_dotenv()

jwt = JWTManager()
db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=3600)  # expira en 1 hora
    
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    @jwt.expired_token_loader
    def token_expirado(jwt_header, jwt_payload):
        return jsonify({
            "error": "El token ha expirado",
            "mensaje": "Por favor, iniciá sesión nuevamente"
        }), 401

    with app.app_context():
        from app import models
        from .routes import productos_bp, auth_bp
        app.register_blueprint(productos_bp)
        app.register_blueprint(auth_bp)
        
        
    return app
__all__ = ['db', 'jwt', 'bcrypt']
