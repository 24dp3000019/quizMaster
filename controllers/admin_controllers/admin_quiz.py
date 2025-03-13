from flask import Blueprint, render_template, redirect, url_for, session,request,flash
from application.database import db
from application.models import Subject,Chapter,Quiz_table,Question_Table,User,Quiz_Attempt_Table,Score_Table
from datetime import datetime
from sqlalchemy.exc import IntegrityError

adminManagingQuiz_bp = Blueprint('adminManagingQuiz', __name__, url_prefix='/admin')


def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            session.clear()  # Clear session for security
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper




@adminManagingQuiz_bp.route('/add_quiz', methods=['GET', 'POST'])
@admin_required
def add_quiz():
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        quiz_name = request.form.get('quiz_name')
        time_duration = request.form.get('time_duration')  # Get time duration from form
        remarks = request.form.get('remarks')
        quiz_date = request.form.get('quiz_date')  # Get quiz date from form

        if chapter_id and quiz_name and time_duration and quiz_date:
            # Check if the quiz name already exists under the selected chapter
            existing_quiz = Quiz_table.query.filter_by(chapter_id=chapter_id, quiz_name=quiz_name).first()
            if existing_quiz:
                return render_template('error_page.html', message="Quiz name already exists under this chapter!")

            # Create a new quiz entry
            new_quiz = Quiz_table(
                chapter_id=chapter_id, 
                quiz_name=quiz_name, 
                time_duration=int(time_duration),  # Ensure it's an integer
                remarks=remarks,
                quiz_date=datetime.strptime(quiz_date, "%Y-%m-%d").date()  # Convert string to date
            )
            db.session.add(new_quiz)
            db.session.commit()
            return render_template('success_page.html', message="Quiz added successfully!")

    chapters = Chapter.query.all()  # Fetch chapters from the database
    return render_template('admin_templates/add_quiz.html', chapters=chapters)


@adminManagingQuiz_bp.route('/view_quiz',methods=['GET','POST'])
@admin_required
def view_quiz():
    quizzes = Quiz_table.query.all() 
    active_users = User.query.count()
    return render_template('admin_templates/viewquiz.html', active_users = active_users ,quizzes=quizzes) 


@adminManagingQuiz_bp.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz_table.query.get_or_404(quiz_id)
    chapters = Chapter.query.all()  # Fetch available chapters

    if request.method == 'POST':
        quiz.chapter_id = request.form['chapter_id']
        quiz.quiz_name = request.form['quiz_name']
        quiz.time_duration = int(request.form['time_duration'])
        quiz.remarks = request.form.get('remarks')
        quiz.quiz_date = datetime.strptime(request.form['quiz_date'], "%Y-%m-%d").date()  # Convert string to date

        # Check if quiz name already exists under the selected chapter
        existing_quiz = Quiz_table.query.filter(
            Quiz_table.chapter_id == quiz.chapter_id, 
            Quiz_table.quiz_name == quiz.quiz_name, 
            Quiz_table.id != quiz.id  # Exclude the current quiz
        ).first()

        if existing_quiz:
            return render_template('error_page.html', message="Quiz name already exists under this chapter!")

        db.session.commit()
        return redirect(url_for('adminManagingQuiz.view_quiz'))

    return render_template('admin_templates/edit_quiz.html', quiz=quiz, chapters=chapters)


@adminManagingQuiz_bp.route('/delete_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz_table.query.get_or_404(quiz_id)

    # Delete all questions associated with the quiz
    Question_Table.query.filter_by(quiz_id=quiz.id).delete()

    # Delete the quiz itself
    db.session.delete(quiz)
    db.session.commit()
    
    flash("Quiz and its questions deleted successfully!", "danger")
    return redirect(url_for('adminManagingQuiz.view_quiz'))

