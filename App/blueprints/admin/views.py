from flask import (
    Blueprint,
    redirect,
    request,
    flash,
    url_for,
    render_template)
from flask_login import login_required, current_user
from sqlalchemy import text

from App.blueprints.admin.models import Dashboard
from App.blueprints.user.decorators import role_required
from App.blueprints.user.models import User
from App.blueprints.coman.models import Coman

from App.blueprints.admin.forms import (
    SearchForm,
    BulkDeleteForm,
    UserForm
)

admin = Blueprint('admin', __name__,
                  template_folder='templates', url_prefix='/admin')


@admin.before_request
@login_required
@role_required('admin')
def before_request():
    """ Protect all of the admin endpoints. """
    pass


# Dashboard -------------------------------------------------------------------
@admin.route('')
def dashboard():
    group_and_count_users = Dashboard.group_and_count_users()

    return render_template('admin/page/dashboard.html',
                           group_and_count_users=group_and_count_users)


# Users -----------------------------------------------------------------------
@admin.route('/users', defaults={'page': 1})
@admin.route('/users/page/<int:page>')
def users(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = User.sort_by(request.args.get('sort', 'created_on'),
                           request.args.get('direction', 'desc'))
    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    paginated_users = User.query \
        .filter(User.search(request.args.get('q', text('')))) \
        .order_by(User.role.asc(), text(order_values)) \
        .paginate(page, 50, True)

    return render_template('admin/user/index.html',
                           form=search_form, bulk_form=bulk_form,
                           users=paginated_users)


@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def users_edit(id):
    user = User.query.get(id)
    form = UserForm(obj=user)

    if form.validate_on_submit():
        if User.is_last_admin(user,
                              request.form.get('role'),
                              request.form.get('active')):
            flash('You are the last admin, you cannot do that.', 'error')
            return redirect(url_for('admin.users'))

        form.populate_obj(user)

        if not user.username:
            user.username = None

        user.save()

        flash('User has been saved successfully.', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user/edit.html', form=form, user=user)


@admin.route('/users/bulk_delete', methods=['POST'])
def users_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = User.get_bulk_action_ids(request.form.get('scope'),
                                       request.form.getlist('bulk_ids'),
                                       omit_ids=[current_user.id],
                                       query=request.args.get('q', text('')))

        delete_count = User.bulk_delete(ids)

        flash('{0} user(s) were scheduled to be deleted.'.format(delete_count),
              'success')
    else:
        flash('No users were deleted, something went wrong.', 'error')

    return redirect(url_for('admin.users'))

@admin.route('/coman', defaults={'page': 1})
@admin.route('/coman/page/<int:page>')
def coman(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = Coman.sort_by(request.args.get('sort', 'created_on'),
                           request.args.get('direction', 'desc'))
    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    paginated_comans = Coman.query \
        .filter(Coman.search(request.args.get('q', text('')))) \
        .order_by(Coman.name.asc(), text(order_values)) \
        .paginate(page, 25, True)

    return render_template('admin/coman/index.html',
                           form=search_form, bulk_form=bulk_form,
                           coman=paginated_comans)


@admin.route('/coman/bulk_delete', methods=['POST'])
def coman_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = Coman.get_bulk_action_ids(request.form.get('scope'),
                                       request.form.getlist('bulk_ids'),
                                       omit_ids=[current_user.id],
                                       query=request.args.get('q', text('')))

        delete_count = Coman.bulk_delete(ids)

        flash('{0} coman(s) were scheduled to be deleted.'.format(delete_count),
              'success')
    else:
        flash('No coman were deleted, something went wrong.', 'error')

    return redirect(url_for('admin.coman'))
