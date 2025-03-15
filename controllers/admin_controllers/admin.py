from flask import Blueprint, render_template, redirect, url_for, session
from application.models import User, Subject, Quiz_table, Question_Table,Chapter


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
   
    if not session.get('user_id') or not session.get('is_admin'):
        session.clear()  
        return redirect(url_for('auth.login'))

   
    active_users = User.query.count()
    total_subjects = Subject.query.count()
    total_chapters=Chapter.query.count()
    total_quizzes = Quiz_table.query.count()
    total_questions = Question_Table.query.count()

    return render_template(
        'admin_templates/admin_dashboard.html',
        active_users=active_users,
        total_subjects=total_subjects,total_chapters=total_chapters,
        total_quizzes=total_quizzes,
        total_questions=total_questions
    )


