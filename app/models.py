from sqlalchemy import ForeignKey
from flask import Flask,Blueprint
from . import db 
from flask_login import UserMixin
import app


class User(db.Model, UserMixin):
    id  = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True , nullable=False)
    passwordHash = db.Column(db.String(500))
    user_type = db.Column(db.Integer)
    reservation_no = db.column(db.Integer,db.ForeignKey("reservation.reservation_no"))
    Reservation = db.relationship("Reservation")
    
    
class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city =  db.Column(db.String(150)) 
    peak_season_rate = db.Column(db.Integer)
    off_peak_season_rate = db.Column(db.Integer)
    number_of_free_rooms =  db.Column(db.Integer)
    total_capacity = db.Column(db.Integer)
    standard_capacity = db.Column(db.Integer)
    double_capacity = db.Column(db.Integer)
    family_capacity = db.Column(db.Integer)

class Reservation(db.Model):
    reservation_no = db.Column(db.Integer,primary_key=True)
    check_in_date = db.Column(db.DateTime)
    check_out_date = db.Column(db.DateTime)
    guest_amount = db.Column(db.Integer)
    total_price = db.Column(db.Integer)
    date_of_reservation = db.Column(db.DateTime)
    room_type = db.Column(db.String(10))
    hotel_id = db.Column(db.Integer, db.ForeignKey("hotel.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    currency_type = db.Column(db.Integer, db.ForeignKey("currency.id"))
    User = db.relationship("User")
    Hotel = db.relationship("Hotel")
    Currency = db.relationship("Currency")
    
class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(10))
    rate = db.Column(db.Float)

