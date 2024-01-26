from crypt import methods
import datetime
import email
from hashlib import new
from nis import cat
import re
from flask import abort, flash, jsonify, render_template, redirect,session, request, url_for, current_app
from flask_login import login_required, login_user, current_user, logout_user
from sqlalchemy import DateTime, true
from .main import app
from flask_session  import Session
from .models import  User, Reservation, Hotel, Currency
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask_admin import Admin, expose,AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import date as date_n
from datetime  import datetime
@app.route("/" )
def homepage():
    return render_template("home.html")

@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/profile" , methods=["GET"])
@login_required
def profile():
    user = User.query.filter_by(id=current_user.id).first()
    if user.user_type ==  1:
        return redirect("/admin/")
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template("profile.html", user=current_user, reservations=reservations)

@app.route("/receipt" , methods=["GET"])
def receipt():
    return render_template("receipt.html")

@app.route("/confirmation",methods=["GET"])
def confirmation():
    return render_template("confirmation.html")

@app.route("/terms",methods=["GET"])
def terms():
    return render_template("terms.html")

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	abort (404)

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    abort (500)



@app.route("/signup", methods=['GET', 'POST'])
@staticmethod
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Email already exists.',category='error')
        elif len(email) < 4:
            flash('Email  must  be greater than 3 characters.',category='error')
        elif password1 != password2: 
            flash('passwords don\'t match.',category='error')   
        elif len (password1) < 8:
            flash('Password must be at least 8 characters')        
        
        new_user = User(email=email, passwordHash=generate_password_hash(password2, method='sha256'), user_type=2)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        db.session.close()
        return redirect("/")
        
    return render_template("signup.html", user=current_user)


@app.route("/login", methods=['POST'])
def login():
    email = request.form.get("email")
    password = request.form.get("password1")
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.passwordHash, password):
        flash('Email does not exist or password is incorrect',category='error')
    
    login_user(user)
    
    return redirect("/")
    

    
@app.route("/logout", methods=['POST'])
def logout():
    logout_user()
    return redirect("/")



@app.route('/api/costs', methods=['POST'])
def costs():
    data = request.get_json()
    start_date = data['checkin']
    guest_amount = int(data['guestamount'])
    checkout = data['checkout']
    city = data['city']
    current_date = datetime.now()
    currency = int(data['currency'])
    
    hotel = Hotel.query.filter_by(city=city).first()
    off_peak = hotel.off_peak_season_rate
    peak = hotel.peak_season_rate
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    checkout = datetime.strptime(checkout, '%Y-%m-%d')
    nights = (checkout - start_date).days

    currency = Currency.query.filter_by(id=currency).first()
    off_peak = off_peak * currency.rate
    peak = peak * currency.rate

    #peak  and off  peak rates   
    if start_date.month in range(4,10):
        if guest_amount == 1:
            cost = off_peak * nights 
            #add room types
        elif guest_amount == 2:
            cost = off_peak * 0.1 * nights + off_peak  * nights 
        else:
            cost = off_peak * 0.5 * nights + off_peak * nights
    else:
        if guest_amount == 1:
            cost =  peak * nights
        elif guest_amount == 2:
            cost =  peak * 0.1 * nights +  peak  * nights
        else:
            cost =  peak * 0.5 * nights +  peak  * nights
        
    #booking  in advance
    if (start_date - current_date).days == 90:
        cost = cost * 0.2 + cost
    elif (start_date - current_date).days == 60:  
        cost = cost * 0.1 + cost
    elif (start_date - current_date).days == 30:  
        cost = cost * 0.05 + cost
        
    return jsonify(cost)


@app.route("/paymentpage", methods=['GET','POST'])
@login_required
def paymentpage():
    if request.method == "POST":
        start_date = request.form.get("checkin")
        checkout = request.form.get("checkout") 
        city = request.form.get("city")
        guest_amount = request.form.get("guestamount")
        reservationdate = datetime.now()
        currency_type = request.form.get("currency")
        hotel = Hotel.query.filter_by(city=city).first()
        current_date = datetime.now()
        
        if guest_amount == "1":
            room_type = "standard"
        elif guest_amount == "2":
            room_type = "double"
        else:
            room_type = "family"
            
        off_peak = hotel.off_peak_season_rate
        peak = hotel.peak_season_rate
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        checkout = datetime.strptime(checkout, '%Y-%m-%d')
        nights = (checkout - start_date).days
        
        currency = Currency.query.filter_by(id=currency_type).first()
        off_peak = off_peak * currency.rate
        peak = peak * currency.rate
            
        if start_date.month in range(4,10):
                if guest_amount == 1:
                    cost = off_peak * nights 
                    #add room types
                elif guest_amount == 2:
                    cost = off_peak * 0.1 * nights + off_peak  * nights 
                else:
                    cost = off_peak * 0.5 * nights + off_peak * nights
        else:
            if guest_amount == 1:
                cost =  peak * nights
            elif guest_amount == 2:
                cost =  peak * 0.1 * nights +  peak  * nights
            else:
                cost =  peak * 0.5 * nights +  peak  * nights
                
        #booking  in advance
        if (start_date - current_date).days in range(80,90):
            cost = cost * 0.2 + cost
        elif (start_date - current_date).days in range(60,79):  
            cost = cost * 0.1 + cost
        elif (start_date - current_date).days in range(45,59):  
            cost = cost * 0.05 + cost
        else:
            cost=cost   
            
        reservation = Reservation(check_in_date=start_date, check_out_date=checkout, room_type=room_type, guest_amount=guest_amount, hotel_id=hotel.id,user_id=current_user.id ,total_price=cost,date_of_reservation=reservationdate, currency_type=currency.id, User=current_user, Hotel=hotel)
        
        db.session.add(reservation)
        db.session.commit()
        db.session.close()
        return redirect("/confirmation")
    return render_template("paymentpage.html" , user=current_user)

