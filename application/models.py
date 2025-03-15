from .database import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    qualification = db.Column(db.String, nullable=False)
    dateofbirth = db.Column(db.Date, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Quiz_table(db.Model):
    __tablename__ = 'quiz_table'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False) 
    quiz_name = db.Column(db.Text,nullable=False)  
    time_duration = db.Column(db.Integer, nullable=False)  
    remarks = db.Column(db.Text) 
    quiz_date = db.Column(db.Date, nullable=False) 
    questions = db.relationship('Question_Table', backref='quiz', lazy=True, cascade="all, delete")

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    quizzes = db.relationship('Quiz_table', backref='chapter', lazy=True)

class Question_Table(db.Model):
    __tablename__ = 'question_table'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz_table.id'), nullable=False)
    question_statement = db.Column(db.String, nullable=False)
    option_1 = db.Column(db.String, nullable=False)
    option_2 = db.Column(db.String, nullable=False)
    option_3 = db.Column(db.String, nullable=False)
    option_4 = db.Column(db.String, nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)
    question_marks = db.Column(db.Integer, nullable=False)

class Quiz_Attempt_Table(db.Model):
    __tablename__ = 'quiz_attempt_table'
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz_table.id'), nullable=False) 
    question_id=db.Column(db.Integer,db.ForeignKey('question_table.id'), nullable=False)
    selected_option = db.Column(db.Integer)
    is_correct = db.Column(db.Boolean)
    question = db.relationship('Question_Table', backref='attempts', lazy=True)

    

class Score_Table(db.Model):
    __tablename__ = 'score_table'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz_table.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    total_score = db.Column(db.Integer, nullable=False)
    total_questions_attempted = db.Column(db.Integer, nullable=False)
    attempt_id = db.Column(db.Integer, nullable=False)  
    correct_answers = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow) 
    end_time = db.Column(db.DateTime,nullable=True)
    