from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.extensions import db
from app.models import Subject

subjects_bp = Blueprint('subjects', __name__, url_prefix='/subjects')


@subjects_bp.route('/')
def subjects_list():
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('subjects.html', subjects=subjects)


@subjects_bp.route('/add', methods=['POST'])
def subject_add():
    name = request.form.get('name', '').strip()
    short_name = request.form.get('short_name', '').strip()

    if not name:
        flash('Название обязательно', 'error')
        return redirect(url_for('subjects.subjects_list'))

    db.session.add(Subject(name=name, short_name=short_name))
    db.session.commit()
    flash('Дисциплина добавлена', 'success')
    return redirect(url_for('subjects.subjects_list'))


@subjects_bp.route('/edit/<int:subject_id>', methods=['POST'])
def subject_edit(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    subject.name = request.form.get('name', subject.name).strip()
    subject.short_name = request.form.get('short_name', subject.short_name)
    db.session.commit()
    flash('Дисциплина обновлена', 'success')
    return redirect(url_for('subjects.subjects_list'))


@subjects_bp.route('/delete/<int:subject_id>', methods=['POST'])
def subject_delete(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Дисциплина удалена', 'success')
    return redirect(url_for('subjects.subjects_list'))