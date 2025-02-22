import click
import random

from datetime import datetime

from faker import Faker

from App.app import create_app
from App.extensions import db
from App.blueprints.user.models import User
from App.blueprints.coman.models import Coman

# Create an app context for the database connection.
app = create_app()
db.app = app

fake = Faker()


def _log_status(count, model_label):
    """
    Log the output of how many records were created.

    :param count: Amount created
    :type count: int
    :param model_label: Name of the model
    :type model_label: str
    :return: None
    """
    click.echo('Created {0} {1}'.format(count, model_label))

    return None


def _bulk_insert(model, data, label):
    """
    Bulk insert data to a specific model and log it. This is much more
    efficient than adding 1 row at a time in a loop.

    :param model: Model being affected
    :type model: SQLAlchemy
    :param data: Data to be saved
    :type data: list
    :param label: Label for the output
    :type label: str
    :return: None
    """
    with app.app_context():
        model.query.delete()
        db.session.commit()
        db.engine.execute(model.__table__.insert(), data)

        _log_status(model.query.count(), label)

    return None


@click.group()
def cli():
    """ Add items to the database. """
    pass


@click.command()
def users():
    """
    Generate fake users.
    """
    random_emails = []
    data = []

    click.echo('Working...')

    # Ensure we get about 100 unique random emails.
    for i in range(0, 99):
        random_emails.append(fake.email())

    random_emails.append(app.config['SEED_ADMIN_EMAIL'])
    random_emails = list(set(random_emails))

    while True:
        if len(random_emails) == 0:
            break

        fake_datetime = fake.date_time_between(
            start_date='-1y', end_date='now').strftime('%s')

        created_on = datetime.utcfromtimestamp(
            float(fake_datetime)).strftime('%Y-%m-%dT%H:%M:%S Z')

        random_percent = random.random()

        if random_percent >= 0.05:
            role = 'member'
        else:
            role = 'admin'

        email = random_emails.pop()

        random_percent = random.random()

        if random_percent >= 0.5:
            random_trail = str(int(round((random.random() * 1000))))
            username = fake.first_name() + random_trail
        else:
            username = None

        fake_datetime = fake.date_time_between(
            start_date='-1y', end_date='now').strftime('%s')

        current_sign_in_on = datetime.utcfromtimestamp(
            float(fake_datetime)).strftime('%Y-%m-%dT%H:%M:%S Z')

        params = {
            'created_on': created_on,
            'updated_on': created_on,
            'role': role,
            'email': email,
            'username': username,
            'password': User.encrypt_password('password'),
            'sign_in_count': random.random() * 100,
            'current_sign_in_on': current_sign_in_on,
            'current_sign_in_ip': fake.ipv4(),
            'last_sign_in_on': current_sign_in_on,
            'last_sign_in_ip': fake.ipv4()
        }

        # Ensure the seeded admin is always an admin with the seeded password.
        if email == app.config['SEED_ADMIN_EMAIL']:
            password = User.encrypt_password(app.config['SEED_ADMIN_PASSWORD'])

            params['role'] = 'admin'
            params['password'] = password

        data.append(params)

    return _bulk_insert(User, data, 'users')


@click.command()
@click.pass_context
def all(ctx):
    """
    Generate all data.

    :param ctx:
    :return: None
    """
    ctx.invoke(users)

    return None


@click.command()
def comans():
     """
     Generate fake comans.
     """
     random_emails = []
     data = []

     click.echo('Working...')

    # Ensure we get about 100 unique random emails.
     for i in range(0, 99):
         random_emails.append(fake.email())

     random_emails.append(app.config['SEED_ADMIN_EMAIL'])
     random_emails = list(set(random_emails))

     while True:
         if len(random_emails) == 0:
             break

         fake_datetimeCreate = fake.date_time_between(
             start_date='-2y', end_date='now').strftime('%s')

         created_on = datetime.utcfromtimestamp(
             float(fake_datetimeCreate)).strftime('%Y-%m-%dT%H:%M:%S Z')

         fake_datetimeUpdated = fake.date_time_between(
         start_date='-1y', end_date='now').strftime('%s')

         updated_on = datetime.utcfromtimestamp(
            float(fake_datetimeUpdated)).strftime('%Y-%m-%dT%H:%M:%S Z')

         random_percent = random.random()

         if random_percent >= 0.05:
             nda = gfsi = organic = kosherCert = halalCert = True
             gmoCert = usadInspect = glutenFreeCert = realChocolate  = True
         else:
             nda = gfsi = organic = kosherCert = halalCert = False
             gmoCert = usadInspect = glutenFreeCert = realChocolate = False

         email = random_emails.pop()

         random_percent = random.random()

         if random_percent >= 0.5:
             random_trail = str(int(round((random.random() * 1000))))
             name = fake.company() + ' ' + random_trail
         else:
             random_trail = str(int(round((random.random() * 2000))))
             name = fake.company() + ' ' + random_trail

         params = {
             'created_on': created_on,
             'updated_on': updated_on,
             'nda': nda,
             'email': email,
             'name': name,
             'state': 'MI',
             'gfsi': gfsi,
             'organic': organic,
             'kosherCert': kosherCert,
             'halalCert': halalCert,
             'gmoCert': gmoCert,
             'usadInspect': usadInspect,
             'glutenFreeCert': glutenFreeCert,
             'realChocolate': realChocolate,
             'address' : '580 Foutain Ave., Brooklyn',
             'city' : 'Lumberton',
             'zip' : int(11368),
             'contact' : 'Donald',
             'contactPosition' : 'President',
             'cellphone' : '718-271-8228',
             'directphone' : '718-272-4242',
             'website' : 'www.azpharmaceutical.com',
             'notes' : fake.text()
            }

         data.append(params)

     return _bulk_insert(Coman, data, 'comans')

cli.add_command(comans)
cli.add_command(users)
cli.add_command(all)
