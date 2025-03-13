from flask import Blueprint, render_template, redirect, url_for, session,request,flash
from application.models import User
from application.models import Subject,Chapter,Quiz_table,Question_Table,User,Quiz_Attempt_Table,Score_Table
from application.database import db
from datetime import datetime,date
from .user import get_quiz_attempts

userProfile_bp = Blueprint('userProfile', __name__, url_prefix='/user')

@userProfile_bp.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return redirect(url_for('auth.login'))

    # Get all unique quiz attempts with attempt_id
    # We'll use a subquery to get the attempt_ids for each quiz
    quiz_attempts = get_quiz_attempts(user.user_id)

    total_quizzes = Quiz_table.query.count()
    return render_template(
        'user_templates/user_profile.html',
        user=user,
        quiz_attempts=quiz_attempts,
        username=user.username,total_quizzes=total_quizzes
    )
