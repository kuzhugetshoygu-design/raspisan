from app.extensions import db

# Ассоциативная таблица: преподаватель <-> дисциплина
teacher_subjects = db.Table(
    'teacher_subjects',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True)
)


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    speciality = db.Column(db.String(100))
    course = db.Column(db.Integer)


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    short_name = db.Column(db.String(20))
    color = db.Column(db.String(20), default='#3498db')

    subjects = db.relationship(
        'Subject',
        secondary=teacher_subjects,
        backref=db.backref('teachers', lazy='dynamic'),
        lazy='dynamic'
    )


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    short_name = db.Column(db.String(20))


class Classroom(db.Model):
    __tablename__ = 'classrooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100))
    type = db.Column(db.String(50))
    seats = db.Column(db.Integer)


class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'))
    day = db.Column(db.String(20))
    week1_lesson = db.Column(db.Integer)
    week2_lesson = db.Column(db.Integer)
    lesson_type = db.Column(db.String(50))

    group = db.relationship('Group')
    teacher = db.relationship('Teacher')
    subject = db.relationship('Subject')
    classroom = db.relationship('Classroom')