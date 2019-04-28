from flask_wtf import Form
from wtforms import HiddenField, StringField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Email
from wtforms.validators import Length, Optional, Regexp
# from wtforms_components import EmailField, Email, Unique

from lib.util_wtforms import ModelForm
from App.blueprints.user.models import User
from App.blueprints.user.validations import ensure_identity_exists, \
    ensure_existing_password_matches


class LoginForm(Form):
    next = HiddenField()
    identity = StringField('Username or email',
                           [DataRequired(), Length(3, 254)])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    # remember = BooleanField('Stay signed in')


class BeginPasswordResetForm(Form):
    identity = StringField('Username or email',
                           [DataRequired(),
                            Length(3, 254),
                            ensure_identity_exists])


class PasswordResetForm(Form):
    reset_token = HiddenField()
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])


class SignupForm(ModelForm):
    email = StringField('Email Address',
                        [DataRequired(), Email(), Length(min=6, max=35)])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])

    def validate_email(self, email):
        """Email validation."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class WelcomeForm(ModelForm):
    username_message = 'Letters, numbers and underscores only please.'

    username = StringField(validators=[
        DataRequired(),
        Length(1, 16),
        Regexp(r'^\w+$', message=username_message)
    ])

    def validate_username(self, username):
        """username validation."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')


class UpdateCredentials(ModelForm):
    current_password = PasswordField('Current password',
                                     [DataRequired(),
                                      Length(8, 128),
                                      ensure_existing_password_matches])

    email = StringField('Email Address',
                        [DataRequired(), Email(), Length(min=6, max=35)])
    password = PasswordField('Password', [Optional(), Length(8, 128)])
