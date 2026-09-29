from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.extensions import db
from app.models import Group, Teacher, Subject, Classroom, Lesson

schedule_bp = Blueprint('schedule', __name__)


@schedule_bp.route('/')
def index():
    groups = Group.query.order_by(Group.name).all()
    teachers = Teacher.query.order_by(Teacher.name).all()
    subjects = Subject.query.order_by(Subject.name).all()
    lessons = Lesson.query.all()

    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    paras = [1, 2, 3, 4]

    schedule = {g.id: {d: {p: [] for p in paras} for d in days} for g in groups}

    for lesson in lessons:
        para = lesson.week1_lesson if lesson.week1_lesson else lesson.week2_lesson
        if para and lesson.group_id in schedule and lesson.day in schedule[lesson.group_id]:
            if para in schedule[lesson.group_id][lesson.day]:
                schedule[lesson.group_id][lesson.day][para].append(lesson)

    lessons_data = {}
    for l in lessons:
        lessons_data[l.id] = {
            'id': l.id,
            'group_id': l.group_id,
            'teacher_id': l.teacher_id,
            'subject_id': l.subject_id,
            'day': l.day,
            'week1_lesson': l.week1_lesson,
            'week2_lesson': l.week2_lesson,
            'classroom': l.classroom.name if l.classroom else '',
            'lesson_type': l.lesson_type or '',
        }

    teachers_data = {}
    for t in teachers:
        teachers_data[t.id] = {
            'id': t.id,
            'name': t.name,
            'short_name': t.short_name,
            'color': t.color,
            'subjects': [{'id': s.id, 'name': s.name, 'short_name': s.short_name} for s in t.subjects]
        }

    from collections import defaultdict
    conflict_ids = set()
    slots = defaultdict(list)
    for l in lessons:
        if l.week1_lesson:
            slots[('w1', l.day, l.week1_lesson)].append(l)
        if l.week2_lesson:
            slots[('w2', l.day, l.week2_lesson)].append(l)
    for key, group in slots.items():
        for attr in ('group_id', 'teacher_id', 'classroom_id'):
            buckets = defaultdict(list)
            for l in group:
                val = getattr(l, attr)
                if val:
                    buckets[val].append(l)
            for val, lst in buckets.items():
                if len(lst) > 1:
                    for l in lst:
                        conflict_ids.add(l.id)

    return render_template(
        'index.html',
        groups=groups,
        teachers=teachers,
        subjects=subjects,
        schedule=schedule,
        days=days,
        paras=paras,
        lessons_data=lessons_data,
        teachers_data=teachers_data,
        conflict_ids=conflict_ids
    )


@schedule_bp.route('/lessons/add', methods=['POST'])
def lesson_add():
    group_id = request.form.get('group_id')
    teacher_id = request.form.get('teacher_id')
    subject_id = request.form.get('subject_id')
    day = request.form.get('day')
    week1_lesson = request.form.get('week1_lesson') or None
    week2_lesson = request.form.get('week2_lesson') or None
    classroom = request.form.get('classroom', '').strip()
    lesson_type = request.form.get('lesson_type', '').strip()

    if not (group_id and teacher_id and subject_id and day):
        flash('Заполните обязательные поля', 'error')
        return redirect(url_for('schedule.index'))

    for c in Lesson.query.filter(Lesson.teacher_id == teacher_id, Lesson.day == day,
                                  Lesson.group_id != group_id).all():
        if (week1_lesson and str(c.week1_lesson) == str(week1_lesson)) or \
           (week2_lesson and str(c.week2_lesson) == str(week2_lesson)):
            flash('Конфликт: преподаватель уже занят в этот день и пару', 'error')
            return redirect(url_for('schedule.index'))

    for c in Lesson.query.filter(Lesson.group_id == group_id, Lesson.day == day).all():
        if (week1_lesson and str(c.week1_lesson) == str(week1_lesson)) or \
           (week2_lesson and str(c.week2_lesson) == str(week2_lesson)):
            flash('Конфликт: у группы уже есть занятие в этот день и пару', 'error')
            return redirect(url_for('schedule.index'))

    classroom_id = None
    if classroom:
        cab = Classroom.query.filter_by(name=classroom).first()
        if cab:
            classroom_id = cab.id
            for c in Lesson.query.filter(Lesson.classroom_id == cab.id, Lesson.day == day).all():
                if (week1_lesson and str(c.week1_lesson) == str(week1_lesson)) or \
                   (week2_lesson and str(c.week2_lesson) == str(week2_lesson)):
                    flash(f'Конфликт кабинета: {classroom} уже занят в этот день и пару', 'error')
                    return redirect(url_for('schedule.index'))
        else:
            cab = Classroom(name=classroom)
            db.session.add(cab)
            db.session.commit()
            classroom_id = cab.id

    lesson = Lesson(
        group_id=int(group_id),
        teacher_id=int(teacher_id),
        subject_id=int(subject_id),
        classroom_id=classroom_id,
        day=day,
        week1_lesson=int(week1_lesson) if week1_lesson else None,
        week2_lesson=int(week2_lesson) if week2_lesson else None,
        lesson_type=lesson_type or None
    )
    db.session.add(lesson)
    db.session.commit()
    flash('Занятие добавлено', 'success')
    return redirect(url_for('schedule.index'))


@schedule_bp.route('/lessons/edit/<int:lesson_id>', methods=['POST'])
def lesson_edit(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    group_id = request.form.get('group_id')
    teacher_id = request.form.get('teacher_id')
    subject_id = request.form.get('subject_id')
    day = request.form.get('day')
    week1_lesson = request.form.get('week1_lesson') or None
    week2_lesson = request.form.get('week2_lesson') or None
    classroom = request.form.get('classroom', '').strip()
    lesson_type = request.form.get('lesson_type', '').strip()

    for c in Lesson.query.filter(Lesson.id != lesson.id, Lesson.group_id == group_id,
                                  Lesson.day == day).all():
        if (week1_lesson and str(c.week1_lesson) == str(week1_lesson)) or \
           (week2_lesson and str(c.week2_lesson) == str(week2_lesson)):
            flash('Конфликт: у группы уже есть занятие', 'error')
            return redirect(url_for('schedule.index'))

    for c in Lesson.query.filter(Lesson.id != lesson.id, Lesson.teacher_id == teacher_id,
                                  Lesson.day == day).all():
        if (week1_lesson and str(c.week1_lesson) == str(week1_lesson)) or \
           (week2_lesson and str(c.week2_lesson) == str(week2_lesson)):
            flash('Конфликт: преподаватель уже занят', 'error')
            return redirect(url_for('schedule.index'))

    lesson.group_id = int(group_id)
    lesson.teacher_id = int(teacher_id)
    lesson.subject_id = int(subject_id)
    lesson.day = day
    lesson.week1_lesson = int(week1_lesson) if week1_lesson else None
    lesson.week2_lesson = int(week2_lesson) if week2_lesson else None
    lesson.lesson_type = lesson_type or None

    if classroom:
        cab = Classroom.query.filter_by(name=classroom).first()
        if cab:
            for c in Lesson.query.filter(Lesson.id != lesson.id, Lesson.classroom_id == cab.id,
                                          Lesson.day == day).all():
                if (week1_lesson and str(c.week1_lesson) == str(week1_lesson)) or \
                   (week2_lesson and str(c.week2_lesson) == str(week2_lesson)):
                    flash(f'Конфликт кабинета: {classroom} уже занят', 'error')
                    return redirect(url_for('schedule.index'))
            lesson.classroom_id = cab.id
        else:
            cab = Classroom(name=classroom)
            db.session.add(cab)
            db.session.commit()
            lesson.classroom_id = cab.id
    else:
        lesson.classroom_id = None

    db.session.commit()
    flash('Занятие обновлено', 'success')
    return redirect(url_for('schedule.index'))


@schedule_bp.route('/lessons/delete/<int:lesson_id>', methods=['POST'])
def lesson_delete(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    db.session.delete(lesson)
    db.session.commit()
    flash('Занятие удалено', 'success')
    return redirect(url_for('schedule.index'))


@schedule_bp.route('/lessons/move', methods=['POST'])
def lesson_move():
    data = request.get_json()
    lesson = Lesson.query.get_or_404(int(data['lesson_id']))
    new_group_id = int(data['group_id'])
    new_day = data['day']
    new_para = int(data['para'])

    old_group_id, old_day = lesson.group_id, lesson.day
    old_para = lesson.week1_lesson or lesson.week2_lesson

    if (old_group_id == new_group_id and old_day == new_day and old_para == new_para):
        return {'status': 'ok', 'week1': lesson.week1_lesson, 'week2': lesson.week2_lesson}

    target = 'week1_lesson' if lesson.week1_lesson else 'week2_lesson'

    for c in Lesson.query.filter(Lesson.id != lesson.id, Lesson.group_id == new_group_id,
                                  Lesson.day == new_day).all():
        if getattr(c, target) == new_para:
            return {'status': 'conflict', 'message': 'У группы уже есть занятие в этот день и пару'}

    for c in Lesson.query.filter(Lesson.id != lesson.id, Lesson.teacher_id == lesson.teacher_id,
                                  Lesson.day == new_day).all():
        if getattr(c, target) == new_para:
            return {'status': 'conflict', 'message': 'Преподаватель уже занят в этот день и пару'}

    if lesson.classroom_id:
        for c in Lesson.query.filter(Lesson.id != lesson.id,
                                      Lesson.classroom_id == lesson.classroom_id,
                                      Lesson.day == new_day).all():
            if getattr(c, target) == new_para:
                cab = Classroom.query.get(lesson.classroom_id)
                return {'status': 'conflict',
                        'message': f'Кабинет {cab.name if cab else ""} уже занят в этот день и пару'}

    setattr(lesson, target, new_para)
    lesson.group_id = new_group_id
    lesson.day = new_day
    db.session.commit()

    return {'status': 'ok', 'week1': lesson.week1_lesson, 'week2': lesson.week2_lesson}




@schedule_bp.route('/print/group/<int:group_id>')
def print_group(group_id):
    group = Group.query.get_or_404(group_id)
    lessons = Lesson.query.filter_by(group_id=group_id).all()
    teachers = Teacher.query.all()
    subjects = Subject.query.all()
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    paras = [1, 2, 3, 4]

    schedule = {d: {p: {'w1': None, 'w2': None} for p in paras} for d in days}

    for lesson in lessons:
        if lesson.day not in schedule:
            continue
        if lesson.week1_lesson and lesson.week1_lesson in paras:
            schedule[lesson.day][lesson.week1_lesson]['w1'] = lesson
        if lesson.week2_lesson and lesson.week2_lesson in paras:
            schedule[lesson.day][lesson.week2_lesson]['w2'] = lesson

    return render_template(
        'print_group.html',
        group=group,
        schedule=schedule,
        days=days,
        paras=paras,
        teachers=teachers,
        subjects=subjects
    )


@schedule_bp.route('/print/all')
def print_all():
    groups = Group.query.order_by(Group.name).all()
    teachers = Teacher.query.all()
    subjects = Subject.query.all()
    lessons = Lesson.query.all()
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    paras = [1, 2, 3, 4]

    # schedule[group_id][day][para] = список занятий
    schedule = {g.id: {d: {p: [] for p in paras} for d in days} for g in groups}

    for lesson in lessons:
        para = lesson.week1_lesson if lesson.week1_lesson else lesson.week2_lesson
        if para and lesson.group_id in schedule and lesson.day in schedule[lesson.group_id]:
            if para in schedule[lesson.group_id][lesson.day]:
                schedule[lesson.group_id][lesson.day][para].append(lesson)

    return render_template(
        'print_all.html',
        groups=groups,
        teachers=teachers,
        subjects=subjects,
        schedule=schedule,
        days=days,
        paras=paras
    )