from flask import Blueprint, render_template, redirect, url_for, session,request,flash
from application.database import db
from application.models import Subject,Chapter,Quiz_table,Question_Table,User,Quiz_Attempt_Table,Score_Table
from datetime import datetime
from sqlalchemy.exc import IntegrityError



adminManagingSub_bp = Blueprint('adminManagingSub', __name__, url_prefix='/admin')

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            session.clear()  # Clear session for security
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@adminManagingSub_bp.route('/create_subject',methods=['GET','POST'])
@admin_required
def create_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
    
        new_subject = Subject(name=name, description=description)
        sub=Subject.query.filter_by(name=name).first()

        if sub:
            return render_template('error.html',message="subject already exists ")
        db.session.add(new_subject)
        db.session.commit()

        return render_template('success_page.html',message='subject succesfully added')
    
    return render_template('admin_templates/create_subjects.html')


@adminManagingSub_bp.route('/view_subjects',methods=['GET','POST'])
@admin_required
def view_subjects():
    subjects = Subject.query.all()
    active_users = User.query.count()
    return render_template('admin_templates/viewSubjects.html',active_users = active_users , subjects=subjects)

@adminManagingSub_bp.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        new_name = request.form['name']
        new_description = request.form['description']

        # Check if the subject name already exists
        existing_subject = Subject.query.filter_by(name=new_name).first()
        if existing_subject and existing_subject.id != subject_id:
            flash('Subject name already exists!', 'danger')
            return redirect(url_for('adminManaging.edit_subject', subject_id=subject_id))

        # Update subject details
        subject.name = new_name
        subject.description = new_description
        db.session.commit()

        flash('Subject updated successfully!', 'success')
        return redirect(url_for('adminManagingSub.view_subjects'))

    return render_template('admin_templates/edit_subject.html', subject=subject)

@adminManagingSub_bp.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    # Delete all related data manually
    for chapter in subject.chapters:
        for quiz in chapter.quizzes:
            Question_Table.query.filter_by(quiz_id=quiz.id).delete()
            Quiz_Attempt_Table.query.filter_by(quiz_id=quiz.id).delete()
            Score_Table.query.filter_by(quiz_id=quiz.id).delete()
            db.session.delete(quiz)

        db.session.delete(chapter)

    db.session.delete(subject)
    db.session.commit()

    flash('Subject and all related data deleted successfully!', 'success')
    return redirect(url_for('adminManagingSub.view_subjects'))
