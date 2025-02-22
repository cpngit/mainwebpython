from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms_alchemy.validators import Unique
from wtforms_components import EmailField, Email

from config.settings import LANGUAGES
from lib.util_wtforms import ModelForm, choices_from_dict
from App.blueprints.user.models import User
from App.blueprints.user.validations import ensure_identity_exists, \
    ensure_existing_password_matches


class LoginForm(FlaskForm):
    next = HiddenField()
    identity = StringField('Username or email',
                           [DataRequired(), Length(3, 254)])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    # remember = BooleanField('Stay signed in')


class BeginPasswordResetForm(FlaskForm):
    identity = StringField('Username or email',
                           [DataRequired(),
                            Length(3, 254),
                            ensure_identity_exists])


class PasswordResetForm(FlaskForm):
    reset_token = HiddenField()
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])


class SignupForm(ModelForm):
    email = EmailField(validators=[
        DataRequired(),
        Email(),
        Unique(User.email)
    ])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])


class WelcomeForm(ModelForm):
    username_message = 'Letters, numbers and underscores only please.'

    username = StringField(validators=[
        Unique(User.username),
        DataRequired(),
        Length(1, 16),
        Regexp(r'^\w+$', message=username_message)
    ])


class UpdateCredentialsForm(ModelForm):
    current_password = PasswordField('Current password',
                                     [DataRequired(),
                                      Length(8, 128),
                                      ensure_existing_password_matches])

    email = EmailField(validators=[
        Email(),
        Unique(User.email)
    ])
    password = PasswordField('Password', [Optional(), Length(8, 128)])


class UpdateLocaleForm(FlaskForm):
    locale = SelectField('Language preference', [DataRequired()],
                         choices=choices_from_dict(LANGUAGES,
                                                   prepend_blank=False))
