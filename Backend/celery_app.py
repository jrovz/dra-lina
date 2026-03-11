"""
Celery application factory.
Usage: celery -A celery_app.celery worker --loglevel=info
"""
from celery import Celery


def make_celery(app=None):
    if app is None:
        from app import create_app
        app = create_app()

    celery = Celery(app.import_name)
    celery.config_from_object({
        'broker_url': app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        'result_backend': app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        'task_serializer': 'json',
        'result_serializer': 'json',
        'accept_content': ['json'],
        'timezone': 'America/Bogota',
        'task_track_started': True,
    })
    celery.set_default()

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery()
