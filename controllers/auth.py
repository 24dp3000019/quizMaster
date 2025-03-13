from flask import Flask, render_template, request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
from application.models import User
from application.database import db
from datetime import datetime
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)



@auth_bp.route("/register",methods=["GET","POST"])
def register():
    if request.method=='POST':
        username=request.form["username"]
        password=request.form["password"]
        fullname=request.form["fullname"]
        qualification=request.form["qualification"]
        dateofbirth = datetime.strptime(request.form["dateofbirth"], "%Y-%m-%d").date() 

        user=User.query.filter_by(username=username).first()

        if user:
            return render_template('error.html',message="username already exists")

        newuser=User(username=username, password=password, fullname=fullname, qualification=qualification, dateofbirth=dateofbirth)
        db.session.add(newuser)
        db.session.commit()
        return render_template('login.html', user=newuser)
    return render_template('registration.html')

@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.username  # Use username instead of user_id
            session['is_admin'] = user.is_admin

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('userDashboard.dashboard', username=user.username))  # Pass username

        else:
            return render_template('error.html', message="Wrong details, please try again.")

    return render_template('login.html')


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
