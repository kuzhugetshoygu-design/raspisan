from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.extensions import db
from app.models import Teacher, Subject

teachers_bp = Blueprint('teachers', __name__, url_prefix='/teachers')


@teachers_bp.route('/')
def teachers_list():
    teachers = Teacher.query.order_by(Teacher.name).all()
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('teachers.html', teachers=teachers, subjects=subjects)


@teachers_bp.route('/add', methods=['POST'])
def teacher_add():
    name = request.form.get('name', '').strip()
    short_name = request.form.get('short_name', '').strip()
    color = request.form.get('color', '#3498db')
    subject_ids = request.form.getlist('subject_ids')

    if not name:
        flash('ФИО преподавателя обязательно', 'error')
        return redirect(url_for('teachers.teachers_list'))

    teacher = Teacher(name=name, short_name=short_name, color=color)

    if subject_ids:
        subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
        for s in subjects:
            teacher.subjects.append(s)

    db.session.add(teacher)
    db.session.commit()
    flash('Преподаватель добавлен', 'success')
    return redirect(url_for('teachers.teachers_list'))


@teachers_bp.route('/edit/<int:teacher_id>', methods=['POST'])
def teacher_edit(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    teacher.name = request.form.get('name', teacher.name).strip()
    teacher.short_name = request.form.get('short_name', teacher.short_name)
    teacher.color = request.form.get('color', teacher.color)

    subject_ids = request.form.getlist('subject_ids')
    teacher.subjects = []
    if subject_ids:
        teacher.subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()

    db.session.commit()
    flash('Преподаватель обновлён', 'success')
    return redirect(url_for('teachers.teachers_list'))


@teachers_bp.route('/delete/<int:teacher_id>', methods=['POST'])
def teacher_delete(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Преподаватель удалён', 'success')
    return redirect(url_for('teachers.teachers_list'))