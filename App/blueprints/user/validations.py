from wtforms.validators import ValidationError

from App.blueprints.user.models import User


def ensure_identity_exists(form, field):
    """
    Ensure an identity exists.

    :param form: wtforms Instance
    :param field: Field being passed in
    :return: None
    """
    user = User.find_by_identity(field.data)

    if not user:
        raise ValidationError('Unable to locate account.')


def ensure_existing_password_matches(form, field):
    """
    Ensure that the current password matches their existing password.

    :param form: wtforms Instance
    :param field: Field being passed in
    :return: None
    """
    user = User.query.get(form._obj.id)

    if not user.authenticated(password=field.data):
        raise ValidationError('Does not match.')
