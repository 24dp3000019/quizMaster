from flask import Blueprint, render_template, redirect, url_for, session,request,flash
from application.models import User
from application.models import Subject,Chapter,Quiz_table,Question_Table,User,Quiz_Attempt_Table,Score_Table
from application.database import db
from datetime import datetime,date
from .user import get_quiz_attempts

userSubjects_bp = Blueprint('userSubjects', __name__, url_prefix='/user')




@userSubjects_bp.route('/subjects/<username>')
def subjects(username):
    user = User.query.filter_by(username=username).first()
    subjects = Subject.query.all()
    active_users = User.query.count()
    current_date = date.today()
    quiz_attempts = get_quiz_attempts(user.user_id)
    
   
    
    return render_template(
        'user_templates/user_subjects.html', 
        username=username, 
        active_users=active_users, 
        subjects=subjects, 
        current_date=current_date, 
        quiz_attempts=quiz_attempts
    )


