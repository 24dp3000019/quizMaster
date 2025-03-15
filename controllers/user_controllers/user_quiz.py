from flask import Blueprint, render_template, redirect, url_for, session,request,flash
from application.models import User
from application.models import Subject,Chapter,Quiz_table,Question_Table,User,Quiz_Attempt_Table,Score_Table
from application.database import db
from datetime import datetime,date
from .user import get_quiz_attempts


userQuiz_bp = Blueprint('userQuiz', __name__, url_prefix='/user')



@userQuiz_bp.route('/progress/<username>')
def quiz(username):
    user = User.query.filter_by(username=username).first()
    quizzes = Quiz_table.query.all() 
    active_users = User.query.count()    
    current_date = date.today()
    quiz_attempts = get_quiz_attempts(user.user_id)
    return render_template('user_templates/user_quiz.html',username=username, active_users = active_users ,quizzes=quizzes,current_date=current_date,quiz_attempts=quiz_attempts) 




@userQuiz_bp.route('/quiz/attempt/<int:quiz_id>/<username>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id, username):
    user = User.query.filter_by(username=username).first_or_404()
    quiz = Quiz_table.query.get_or_404(quiz_id)
    questions = Question_Table.query.filter_by(quiz_id=quiz_id).all()

    
    if quiz.quiz_date != date.today():
        return render_template('error.html', message="You can only attempt this quiz on the scheduled date!")

    if request.method == 'POST':
        results = []
        total_questions = len(questions)
        correct_answers = 0  

       
        last_attempt = Quiz_Attempt_Table.query.filter_by(user_id=user.user_id, quiz_id=quiz_id).order_by(
            Quiz_Attempt_Table.attempt_id.desc()).first()
        current_attempt_id = (last_attempt.attempt_id + 1) if last_attempt else 1

      
        attempts = []
        for question in questions:
            user_answer = request.form.get(f"question_{question.id}")
            correct_option = question.correct_option  
            is_correct = user_answer and int(user_answer) == correct_option

            if is_correct:
                correct_answers +=  question.question_marks

            attempts.append(Quiz_Attempt_Table(
                attempt_id=current_attempt_id,
                user_id=user.user_id, 
                quiz_id=quiz_id, 
                question_id=question.id, 
                selected_option=int(user_answer) if user_answer else None, 
                is_correct=is_correct
            ))

            results.append({
                'question': question.question_statement,
                'user_answer': user_answer if user_answer else "No Answer",
                'correct_answer': correct_option,
                'is_correct': is_correct
            })

        db.session.bulk_save_objects(attempts)  

        
        score_entry = Score_Table(
            quiz_id=quiz_id, 
            user_id=user.user_id, 
            attempt_id=current_attempt_id,  
            total_score=correct_answers, 
            total_questions_attempted=total_questions, 
            correct_answers=correct_answers,
            start_time=datetime.utcnow(), 
            end_time=datetime.utcnow()
        )
        db.session.add(score_entry)
        db.session.commit()

        
        past_attempts = Score_Table.query.filter_by(user_id=user.user_id, quiz_id=quiz_id).order_by(
            Score_Table.attempt_id.desc()).all()

        total_marks = sum(question.question_marks for question in questions)

        quiz_attempts = get_quiz_attempts(user.user_id)
        return render_template(
                'user_templates/quiz_results.html', 
                quiz=quiz, 
                results=results, 
                correct_answers=correct_answers, 
                total_marks=total_marks, 
                username=username, 
                attempt_id=current_attempt_id, 
                past_attempts=past_attempts,quiz_attempts=quiz_attempts
            )

    quiz_attempts = get_quiz_attempts(user.user_id)
    return render_template('user_templates/attempt_quiz.html', quiz=quiz, questions=questions, username=username,quiz_attempts=quiz_attempts)


@userQuiz_bp.route('/quiz/<int:quiz_id>/view/<username>/<int:attempt_id>')
def view_quiz(quiz_id, username, attempt_id):
    user = User.query.filter_by(username=username).first()

    if not user:
        return redirect(url_for('auth.login'))  

    quiz = Quiz_table.query.get_or_404(quiz_id)

    quiz_attempts = db.session.query(
        Question_Table.question_statement,
        Question_Table.option_1,
        Question_Table.option_2,
        Question_Table.option_3,
        Question_Table.option_4,
        Question_Table.correct_option,
        Question_Table.question_marks,
        Quiz_Attempt_Table.selected_option,
        Quiz_Attempt_Table.is_correct
    ).join(Quiz_Attempt_Table, Question_Table.id == Quiz_Attempt_Table.question_id
    ).filter(
        Quiz_Attempt_Table.quiz_id == quiz_id,
        Quiz_Attempt_Table.user_id == user.user_id,
        Quiz_Attempt_Table.attempt_id == attempt_id
    ).all()

    formatted_results = []
    for attempt in quiz_attempts:
        formatted_results.append({
            "question": attempt.question_statement,
            "options": [attempt.option_1, attempt.option_2, attempt.option_3, attempt.option_4],
            "user_answer": attempt.selected_option,
            "correct_option": attempt.correct_option,
            "is_correct": attempt.is_correct,
            "question_marks": attempt.question_marks
        })

    total_marks = sum(result["question_marks"] for result in formatted_results)
    correct_marks = sum(result["question_marks"] for result in formatted_results if result["is_correct"])
    total_questions = len(formatted_results)
    correct_answers = sum(1 for result in formatted_results if result["is_correct"])

    # Get past quiz performance for chart
    past_attempts = Score_Table.query.filter_by(user_id=user.user_id, quiz_id=quiz_id).order_by(Score_Table.start_time).all()
    quizzes = [f"Attempt {i+1}" for i in range(len(past_attempts))]
    scores = [attempt.total_score for attempt in past_attempts]
    quiz_attempts = get_quiz_attempts(user.user_id)
    return render_template(
        'user_templates/view_quiz.html',
        quiz=quiz,
        user=user,
        quiz_results=formatted_results,
        correct_marks=correct_marks,
        total_marks=total_marks,
        total_questions=total_questions,
        correct_answers=correct_answers,
        username=user.username,
        attempt_id=attempt_id,
        quizzes=quizzes,quiz_attempts=quiz_attempts,
        scores=scores
    )




@userQuiz_bp.route("/todays-quizzes/<username>")
def todays_quizzes(username):
    user = User.query.filter_by(username=username).first()
    today = date.today()  
    chapters = Chapter.query.all() 

    
    todays_chapters = []
    for chapter in chapters:
        todays_quizzes = [quiz for quiz in chapter.quizzes if quiz.quiz_date == today]
        if todays_quizzes:
            todays_chapters.append({"name": chapter.name, "quizzes": todays_quizzes})
    quiz_attempts = get_quiz_attempts(user.user_id)
    return render_template("user_templates/user_todays_quizzes.html", chapters=todays_chapters, username=username,quiz_attempts=quiz_attempts)
