
import logging

from logging.handlers import SMTPHandler

from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.debug import DebuggedApplication
from flask_login import current_user
from flask import Flask, render_template, request
from celery import Celery
import base64

from App.blueprints.admin import admin
from App.blueprints.page import page
from App.blueprints.contact import contact
from App.blueprints.user import user
from App.blueprints.user.models import User


from App.extensions import (
    debug_toolbar,
    mail,
    csrf,
    db,
    login_manager,
    babel
)

CELERY_TASK_LIST = [
    'App.blueprints.contact.tasks',
    'App.blueprints.user.tasks',
]


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
                    include=CELERY_TASK_LIST)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, static_folder='../public', static_url_path='')

    app.config.from_object('config.settings')

    if settings_override:
        app.config.update(settings_override)

    app.logger.setLevel(app.config['LOG_LEVEL'])

    middleware(app)
    error_templates(app)
    exception_handler(app)
    app.register_blueprint(admin)
    app.register_blueprint(page)
    app.register_blueprint(contact)
    app.register_blueprint(user)
    # app.register_blueprint(coman)
    extensions(app)
    authentication(app, User)
    locale(app)

    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app)

    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    debug_toolbar.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)

    return None


def authentication(app, user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = 'user.login'

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)

    # @login_manager.request_loader
    # def load_user_from_request(request):

    #     # first, try to login using the api_key url arg
    #     api_key = request.args.get('api_key')
    #     if api_key:
    #         user = User.query.filter_by(api_key=api_key).first()
    #         if user:
    #             return user

    #     # next, try to login using Basic Auth
    #     api_key = request.headers.get('Authorization')
    #     if api_key:
    #         api_key = api_key.replace('Basic ', '', 1)
    #         try:
    #             api_key = base64.b64decode(api_key)
    #         except TypeError:
    #             pass
    #         user = User.query.filter_by(api_key=api_key).first()
    #         if user:
    #             return user

    #     # finally, return None if both methods did not login the user
    #     return None


def locale(app):
    """
    Initialize a locale for the current request.

    :param app: Flask application instance
    :return: str
    """
    if babel.locale_selector_func is None:
        @babel.localeselector
        def get_locale():
            if current_user.is_authenticated:
                return current_user.locale

            accept_languages = app.config.get('LANGUAGES').keys()
            return request.accept_languages.best_match(accept_languages)


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Swap request.remote_addr with the real IP address even if behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


def error_templates(app):
    """
    Register 0 or more custom error pages (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def render_status(status):
        """
         Render a custom template for a specific status.
           Source: http://stackoverflow.com/a/30108946

         :param status: Status as a written name
         :type status: str
         :return: None
         """
        # Get the status code from the status, default to a 500 so that we
        # catch all types of errors and treat them as a 500.
        code = getattr(status, 'code', 500)
        return render_template('errors/{0}.html'.format(code)), code

    for error in [404, 500]:
        app.errorhandler(error)(render_status)

    return None


def exception_handler(app):
    """
    Register 0 or more exception handlers (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    mail_handler = SMTPHandler((app.config.get('MAIL_SERVER'),
                                app.config.get('MAIL_PORT')),
                               app.config.get('MAIL_USERNAME'),
                               [app.config.get('MAIL_USERNAME')],
                               '[Exception handler] A 5xx was thrown',
                               (app.config.get('MAIL_USERNAME'),
                                app.config.get('MAIL_PASSWORD')),
                               secure=())

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter("""
    Time:               %(asctime)s
    Message type:       %(levelname)s


    Message:

    %(message)s
    """))
    app.logger.addHandler(mail_handler)

    return None
