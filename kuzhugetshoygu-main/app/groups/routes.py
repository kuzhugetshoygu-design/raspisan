from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.extensions import db
from app.models import Group

groups_bp = Blueprint('groups', __name__, url_prefix='/groups')


@groups_bp.route('/')
def groups_list():
    groups = Group.query.order_by(Group.name).all()
    return render_template('groups.html', groups=groups)


@groups_bp.route('/add', methods=['POST'])
def group_add():
    name = request.form.get('name', '').strip()
    speciality = request.form.get('speciality', '').strip()
    course = request.form.get('course', '').strip()

    if not name:
        flash('Название группы обязательно', 'error')
        return redirect(url_for('groups.groups_list'))
    if Group.query.filter_by(name=name).first():
        flash('Такая группа уже есть', 'error')
        return redirect(url_for('groups.groups_list'))

    db.session.add(Group(name=name, speciality=speciality,
                         course=int(course) if course else None))
    db.session.commit()
    flash('Группа добавлена', 'success')
    return redirect(url_for('groups.groups_list'))


@groups_bp.route('/edit/<int:group_id>', methods=['POST'])
def group_edit(group_id):
    group = Group.query.get_or_404(group_id)
    group.name = request.form.get('name', group.name).strip()
    group.speciality = request.form.get('speciality', group.speciality)
    course = request.form.get('course', '')
    group.course = int(course) if course else None
    db.session.commit()
    flash('Группа обновлена', 'success')
    return redirect(url_for('groups.groups_list'))


@groups_bp.route('/delete/<int:group_id>', methods=['POST'])
def group_delete(group_id):
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash('Группа удалена', 'success')
    return redirect(url_for('groups.groups_list'))