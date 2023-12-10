"""Game API server"""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SERVER_NAME"] = "localhost:5000"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db = SQLAlchemy()
db.init_app(app)

migrate = Migrate(app, db)

from routes.games import games_bp

app.register_blueprint(games_bp)
