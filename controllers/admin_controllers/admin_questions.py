from flask import Blueprint, render_template, redirect, url_for, session,request,flash
from application.database import db
from application.models import Subject,Chapter,Quiz_table,Question_Table,User,Quiz_Attempt_Table,Score_Table
from datetime import datetime
from sqlalchemy.exc import IntegrityError

adminManagingQuestions_bp = Blueprint('adminManagingQuestions', __name__, url_prefix='/admin')


def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            session.clear()  # Clear session for security
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@adminManagingQuestions_bp.route('/add_quiz_questions',methods=['GET','POST'])
@admin_required
def add_quiz_questions():
    if request.method == 'POST':
        quiz_id = int(request.form.get('quiz_id', 0))
        question_text = request.form.get('question_statement')
        option_1 = request.form.get('option_1')
        option_2 = request.form.get('option_2')
        option_3 = request.form.get('option_3')
        option_4 = request.form.get('option_4')
        correct_option = int(request.form.get('correct_option', 0))
        question_marks = int(request.form.get('question_marks', 0))

        if quiz_id and question_text and option_1 and option_2 and option_3 and option_4 and correct_option:
            existing_question = Question_Table.query.filter_by(quiz_id=quiz_id, question_statement=question_text).first()
            if existing_question:
                return render_template('error_page.html', message="This question already exists in the selected quiz!")

            new_question = Question_Table(
                quiz_id=quiz_id, 
                question_statement=question_text, 
                option_1=option_1, 
                option_2=option_2, 
                option_3=option_3, 
                option_4=option_4, 
                correct_option=correct_option,
                question_marks=question_marks
            )

            try:
                db.session.add(new_question)
                db.session.commit()
                return render_template('success_page.html', message="Quiz question added successfully!")
            except Exception as e:
                db.session.rollback()
                return render_template('error_page.html', message=f"Error adding question: {str(e)}")

    quizzes = Quiz_table.query.all()  
    return render_template('admin_templates/add_quiz_questions.html', quizzes=quizzes)



@adminManagingQuestions_bp.route('/view_questions',methods=['GET','POST'])
@admin_required
def view_questions():
    questions = db.session.query(
        Question_Table.id, 
        Question_Table.quiz_id, 
        Quiz_table.chapter_id,  # Fetch chapter_id from Quiz_table
        Question_Table.question_statement, 
        Question_Table.option_1, 
        Question_Table.option_2, 
        Question_Table.option_3, 
        Question_Table.option_4, 
        Question_Table.correct_option, 
        Question_Table.question_marks
    ).join(Quiz_table, Quiz_table.id == Question_Table.quiz_id).all()
    active_users = User.query.count()

    return render_template('admin_templates/viewquestions.html',active_users = active_users , questions=questions)



@adminManagingQuestions_bp.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@admin_required
def edit_question(question_id):
    question = Question_Table.query.get_or_404(question_id)

    if request.method == 'POST':
        question.question_statement = request.form['question_statement']
        question.option_1 = request.form['option_1']
        question.option_2 = request.form['option_2']
        question.option_3 = request.form['option_3']
        question.option_4 = request.form['option_4']
        question.correct_option = request.form['correct_option']
        question.question_marks = request.form['question_marks']
        
        db.session.commit()
        flash("Question updated successfully!", "success")
        return redirect(url_for('adminManagingQuestions.view_questions'))

    return render_template('admin_templates/edit_question.html', question=question)


@adminManagingQuestions_bp.route('/delete_question/<int:question_id>', methods=['GET', 'POST'])
@admin_required
def delete_question(question_id):
    question = Question_Table.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    
    flash("Question deleted successfully!", "danger")
    return redirect(url_for('adminManagingQuestions.view_questions'))
