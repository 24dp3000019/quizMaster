from flask import Blueprint, render_template, redirect, url_for, session,request,flash
from application.database import db
from application.models import Subject,Chapter,Quiz_table,Question_Table,User,Quiz_Attempt_Table,Score_Table
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from controllers.user_controllers.user import get_quiz_attempts


adminManaging_bp = Blueprint('adminManaging', __name__, url_prefix='/admin')


def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            session.clear()  # Clear session for security
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


#====================================================MANAGE USERS=========================================================
@adminManaging_bp.route('/manage_users',methods=['GET','POST'])
@admin_required
def manage_users():
    users = User.query.all()  # Fetch all users from the database
    active_users = User.query.count()
    return render_template('admin_templates/manage_users.html',active_users=active_users, users=users)



@adminManaging_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_username = request.form['username']
        new_fullname = request.form['fullname']
        date_input = request.form.get('dateofbirth')
      

        # Check if username already exists (excluding the current user)
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.user_id != user_id:
            flash('Username already exists!', 'danger')
            return redirect(url_for('adminManaging.edit_user', user_id=user_id))

        # Update user details
        user.username = new_username
        user.fullname = new_fullname

        if date_input:
            user.dateofbirth = datetime.strptime(date_input, "%Y-%m-%d").date()



        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('adminManaging.manage_users'))

    return render_template('admin_templates/edit_user.html', user=user)



@adminManaging_bp.route('/view_user/<int:user_id>')
@admin_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)

    # Get quiz attempts with all necessary data
    quiz_attempts = db.session.query(
        Score_Table,
        Quiz_table.quiz_name,
        Quiz_table.id.label('quiz_id')  # Get the quiz ID for calculating total marks
    ).join(
        Quiz_table, Score_Table.quiz_id == Quiz_table.id
    ).filter(
        Score_Table.user_id == user.user_id
    ).all()
    
    # Format the results for template rendering
    formatted_attempts = []
    quizzes = []
    scores = []
    correct_answers = []
    
    for score, quiz_name, quiz_id in quiz_attempts:
        # Calculate total possible marks for this quiz
        total_marks = db.session.query(db.func.sum(Question_Table.question_marks)).filter(
            Question_Table.quiz_id == quiz_id
        ).scalar() or 0
        
        attempt = {
            'quiz_name': quiz_name,
            'attempt_id': score.attempt_id,
            'total_score': score.total_score,
            'total_questions_attempted': score.total_questions_attempted,
            'correct_answers': score.correct_answers,
            'start_time': score.start_time,
            'end_time': score.end_time,
            'total_marks': total_marks  # Add total marks to each attempt
        }
        formatted_attempts.append(attempt)
        quizzes.append(quiz_name)
        scores.append(score.total_score)
        correct_answers.append(score.correct_answers)

    return render_template(
        'admin_templates/view_user.html',
        user=user,
        quiz_attempts=formatted_attempts,
        quizzes=quizzes,
        scores=scores,
        correct_answers=correct_answers
    )
# Delete user
@adminManaging_bp.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Error deleting user.', 'danger')

    return redirect(url_for('adminManaging.manage_users'))



@adminManaging_bp.route('/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        qualification = request.form['qualification']
        dateofbirth = datetime.strptime(request.form['dateofbirth'], "%Y-%m-%d").date()

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('error.html', message="Username already exists")

        new_user = User(username=username, password=password, fullname=fullname, qualification=qualification, dateofbirth=dateofbirth, is_admin=False)

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('adminManaging.manage_users'))

    return render_template('admin_templates/add_user.html')

#====================================================\MANAGE USERS=========================================================

