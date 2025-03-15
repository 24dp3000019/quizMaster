from flask import Blueprint, render_template, redirect, url_for, session,request,flash
from application.models import User
from application.models import Subject,Chapter,Quiz_table,Question_Table,User,Quiz_Attempt_Table,Score_Table
from application.database import db
from datetime import datetime,date


user_bp = Blueprint('user', __name__, url_prefix='/user')



def get_quiz_attempts(user_id):
    return (
        db.session.query(
            Quiz_table.id.label("quiz_id"),
            Quiz_table.quiz_name,
            Score_Table.attempt_id, 
            Score_Table.total_score,
            Score_Table.total_questions_attempted,
            Score_Table.correct_answers,
            Score_Table.start_time,
            Score_Table.end_time
        )
        .join(Score_Table, db.and_(
            Score_Table.quiz_id == Quiz_table.id,
            Score_Table.user_id == user_id
        ))
        .group_by(
            Quiz_table.id,
            Quiz_table.quiz_name,
            Score_Table.attempt_id,
            Score_Table.total_score,
            Score_Table.total_questions_attempted,
            Score_Table.correct_answers,
            Score_Table.start_time,
            Score_Table.end_time
        )
        .order_by(Score_Table.start_time.desc())
        .all()
    )




