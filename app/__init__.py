from curses import flash
from ensurepip import bootstrap
from flask import Flask, abort, redirect,session,flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from flask_admin import Admin,AdminIndexView,expose
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy() 



class MymodelView(ModelView):
    def is_accessible(self):
        if current_user.user_type == 1:
         return True 
        else:
            abort(403)



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'horizon website'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/horizonhotels'
    
    from .models import User,Reservation,Hotel
    
    db.init_app(app)
    app.app_context().push()
    db.create_all()
        
    login_manager = LoginManager()
    login_manager.login_view = "app.home"
    login_manager.init_app(app)
    
    from .main import app as app_blueprint
    app.register_blueprint(app_blueprint)
    
    admin = Admin(app, name="Admin",template_mode='bootstrap4')
    admin.add_view(MymodelView(User, db.session))
    admin.add_view(MymodelView(Hotel, db.session))
    admin.add_view(MymodelView(Reservation, db.session))
    
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    
    return app
 
