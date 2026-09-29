from flask import Flask, render_template
from app.extensions import db


def create_app():
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )
    app.config['SECRET_KEY'] = 'dev-secret-key-change-me'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Регистрируем модули (blueprints)
    from app.groups.routes import groups_bp
    from app.teachers.routes import teachers_bp
    from app.subjects.routes import subjects_bp
    from app.schedule.routes import schedule_bp

    app.register_blueprint(groups_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(schedule_bp)

    with app.app_context():
        from app import models  # noqa
        db.create_all()

    return app