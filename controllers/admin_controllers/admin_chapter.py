from flask import Blueprint, render_template, redirect, url_for, session,request,flash
from application.database import db
from application.models import Subject,Chapter,Quiz_table,Question_Table,User,Quiz_Attempt_Table,Score_Table
from datetime import datetime
from sqlalchemy.exc import IntegrityError


adminManagingChapter_bp = Blueprint('adminManagingChapter', __name__, url_prefix='/admin')



def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            session.clear()  # Clear session for security
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper



@adminManagingChapter_bp.route('/add_chapter',methods=['GET','POST'])
@admin_required
def add_chapter():
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        chapter_name = request.form.get('chapter_name')
        description = request.form.get('description')

        if subject_id and chapter_name:
            existing_chapter = Chapter.query.filter_by(subject_id=subject_id, name=chapter_name).first()
            if existing_chapter:
                return render_template('error.html', message="Chapter name already exists under this subject!")

            new_chapter = Chapter(subject_id=subject_id, name=chapter_name, description=description)
            db.session.add(new_chapter)
            db.session.commit()
            return render_template('success_page.html', message="Chapter added successfully!")

    subjects = Subject.query.all()  # Fetch subjects from the database
    return render_template('admin_templates/add_chapters.html', subjects=subjects)




@adminManagingChapter_bp.route('/view_chapter',methods=['GET','POST'])
@admin_required
def view_chapters():
    chapters = Chapter.query.all() 
    active_users = User.query.count()
    return render_template('admin_templates/viewchapter.html',active_users =active_users , chapters=chapters) 


@adminManagingChapter_bp.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        new_name = request.form['name']
        new_description = request.form['description']

        # Check if the chapter name already exists within the same subject
        existing_chapter = Chapter.query.filter_by(name=new_name, subject_id=chapter.subject_id).first()
        if existing_chapter and existing_chapter.id != chapter_id:
            flash('Chapter name already exists!', 'danger')
            return redirect(url_for('adminManaging.edit_chapter', chapter_id=chapter_id))

        # Update chapter details
        chapter.name = new_name
        chapter.description = new_description
        db.session.commit()

        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('adminManagingChapter.view_chapters', subject_id=chapter.subject_id))

    return render_template('admin_templates/update_chapter.html', chapter=chapter)


@adminManagingChapter_bp.route('/delete_chapter/<int:chapter_id>',methods=['GET','POST'])
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    # Delete all related data manually
    for quiz in chapter.quizzes:
        Question_Table.query.filter_by(quiz_id=quiz.id).delete()
        Quiz_Attempt_Table.query.filter_by(quiz_id=quiz.id).delete()
        Score_Table.query.filter_by(quiz_id=quiz.id).delete()
        db.session.delete(quiz)

    db.session.delete(chapter)
    db.session.commit()

    flash('Chapter and all related data deleted successfully!', 'success')
    return redirect(url_for('adminManagingChapter.view_chapters', subject_id=chapter.subject_id))

