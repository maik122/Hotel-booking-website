from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy

app = Blueprint("app", __name__)


from .models import User,Reservation,Hotel
from app import routes
