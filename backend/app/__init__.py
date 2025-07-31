from flask import Flask, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
import os

load_dotenv()

mysql = MySQL()

def create_app():
    app = Flask(__name__, static_folder="./static", static_url_path="/")
    CORS(app, supports_credentials=True)  #  CORS added to correct app instance

    # Load environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
    
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'



    mysql.init_app(app)
    # ✅ Initialize JWT
    jwt = JWTManager(app)

    # Register your Flask Blueprints
    from .views import main
    from .auth import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    @app.errorhandler(404)
    def not_found(e):
        return send_from_directory(app.static_folder, "index.html")

    # Catch-all route for React client-side routing
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    return app

