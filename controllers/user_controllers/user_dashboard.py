from flask import Blueprint, render_template, redirect, url_for, session,request,flash
from application.models import User
from application.models import Subject,Chapter,Quiz_table,Question_Table,User,Quiz_Attempt_Table,Score_Table
from application.database import db
from datetime import datetime,date


userDashboard_bp = Blueprint('userDashboard', __name__, url_prefix='/user')


@userDashboard_bp.route('/dashboard/<username>')
def dashboard(username):
    # Check if user is logged in and not an admin
    if 'user_id' not in session or  session.get('is_admin'):
        return redirect(url_for('auth.login'))

    # Find the user
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('auth.login'))

    # Fetching quiz attempts and scores for the user
    quiz_attempts = (
        db.session.query(Quiz_table.quiz_name, Score_Table.total_score, Score_Table.start_time)
        .join(Score_Table, Score_Table.quiz_id == Quiz_table.id)
        .filter(Score_Table.user_id == user.user_id)
        .all()
    )

    # Count total subjects
    total_subjects = Subject.query.count()

    # Count total chapters
    total_chapters = Chapter.query.count()

    # Count total available quizzes
    total_quizzes = Quiz_table.query.count()

    return render_template(
        'user_templates/user_dashboard.html',
        username=username,
        quiz_attempts=quiz_attempts,
        total_subjects=total_subjects,
        total_chapters=total_chapters,
        total_quizzes=total_quizzes
    )
