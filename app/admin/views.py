from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    make_response,
    current_app
)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db
from app.admin.forms import (
    ChangeAccountTypeForm,
    ChangeUserEmailForm,
    InviteUserForm,
    NewUserForm,
    UpdateUserForm,
    JsonFileImportForm,
    NewUsefulLinkForm
)

from app.decorators import admin_required
from app.email import send_email
from app.models import EditableHTML, Role, User, UsefulLink

from app.admin.helpers import import_json_file, export_json_file, export_json_file_sample

admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user.id,
            token=token,
            _external=True)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user,
            invite_link=invite_link,
        )
        flash('User {} successfully invited'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template(
        'admin/registered_users.html', users=users, roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Email for user {} successfully changed to {}.'.format(
            user.full_name(), user.email), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'.format(
            user.full_name(), user.role.name), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_user(user_id):
    """Change a template's details."""
    user = User.query.get(user_id)
    if user is None:
        abort(404)

    form = UpdateUserForm(obj=user)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.confirmed = request.form.get("confirmed", False)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully updated.'.format(user.full_name()), 'form-success')

    return render_template(
        'admin/manage_user.html',
        user=user,
        form=form
    )


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200



# USEFUL LINKS
@admin.route('/useful-links')
@login_required
@admin_required
def useful_links():
    """View all useful links."""
    useful_links = UsefulLink.query.all()
    return render_template(
        'admin/useful_links.html', useful_links=useful_links)

@admin.route('/useful-link/<string:useful_link_id>')
@admin.route('/useful-link/<string:useful_link_id>/info')
@login_required
def manage_useful_link(useful_link_id):
    """View site details."""
    useful_link = UsefulLink.query.filter_by(id=useful_link_id).first()
    if useful_link is None:
        abort(404)
    return render_template('admin/manage_useful_link.html', useful_link=useful_link)


@admin.route('/new-useful-link', methods=['GET', 'POST'])
@login_required
@admin_required
def new_useful_link():
    """Create a new site."""
    form = NewUsefulLinkForm()
    if form.validate_on_submit():
        useful_link = UsefulLink(
            name=form.name.data,
            url=form.url.data,
            title=form.title.data,
            short_descr=form.short_descr.data,
            long_descr=form.long_descr.data,
            tooltip=form.tooltip.data,
            img=form.img.data,
            enabled=request.form.get("enabled", False)
        )
        db.session.add(useful_link)
        db.session.commit()

        flash('Link {} has been successfully created'.format(useful_link.name),
              'form-success')
        return redirect(url_for('admin.useful_links'))

    return render_template('admin/new_useful_link.html', form=form)


@admin.route('/useful-link/<int:useful_link_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_useful_link(useful_link_id):
    """Update site details."""
    useful_link = UsefulLink.query.filter_by(id=useful_link_id).first()
    if useful_link is None:
        abort(404)

    form = NewUsefulLinkForm(obj=useful_link)
    #form.set_submit_value("Update")

    if form.validate_on_submit():
        useful_link.name = form.name.data
        useful_link.url = form.url.data
        useful_link.title = form.title.data
        useful_link.short_descr = form.short_descr.data
        useful_link.long_descr = form.long_descr.data
        useful_link.tooltip = form.tooltip.data
        useful_link.img = form.img.data
        useful_link.enabled = request.form.get("enabled", False)
        db.session.add(useful_link)
        db.session.commit()

        flash('Link {} has been successfully updated'.format(useful_link.name),
              'form-success')
        return redirect(url_for('admin.useful_links'))

    return render_template('admin/manage_useful_link.html', useful_link=useful_link, form=form)



@admin.route('/useful-link/<string:useful_link_id>/delete')
@login_required
@admin_required
def delete_useful_link_request(useful_link_id):
    """Request deletion of a site."""
    useful_link = UsefulLink.query.filter_by(id=useful_link_id).first()
    if useful_link is None:
        abort(404)
    return render_template('admin/manage_useful_link.html', useful_link=useful_link)



@admin.route('/useful-link/<string:useful_link_id>/_delete')
@login_required
@admin_required
def delete_useful_link(useful_link_id):
    useful_link = UsefulLink.query.filter_by(id=useful_link_id).first()
    if useful_link:
        db.session.delete(useful_link)
        db.session.commit()
        flash('Successfully deleted link {}.'.format(useful_link.name), 'success')
    else:
        flash('Failed to delete link {}.'.format(useful_link.name), 'error')
    return redirect(url_for('admin.useful_links'))




# IMPORT / EXPORT TASKS
@admin.route('/import-export')
@login_required
def manage_import_export():
    """Manage import and export functions"""
    return render_template('admin/manage_import_export.html')


@admin.route('/import-export/export')
@login_required
def export_functions():
    """Manage export functions"""
    return render_template('admin/manage_import_export.html')

 
@admin.route('/import-export/import', methods=["GET", "POST"])
@login_required
@admin_required
def import_functions():
    """Manage export functions"""
    form = JsonFileImportForm()

    # process the import file
    if request.method == 'POST':
        import_file = form.jsonfile.data
        flash("Importing file {}".format(import_file.filename))
        current_app.logger.debug("Importing inventory file: {}".format(import_file))      
        stats = import_json_file(import_file)  
        return render_template('admin/import_results.html', stats=stats)

    return render_template('admin/manage_import_export.html', form=form)


@admin.route('/import-export/export/json')
@login_required
def export_json():
    """Export the inventory to json format
    { "sites": {},
      "devices": {}
    }
    """
    content = export_json_file()
    filename = "toolbox-export.json"
    response = make_response(content)
    response.headers['Content-Type'] = 'Content-Type: text/plain; charset=UTF-8'
    response.headers["Content-Disposition"] = "attachment; filename=" + filename

    return response


@admin.route('/import-export/import/json-example', methods=['GET'])
@login_required
def import_json_example():
    # download a sample import file
    sample = request.args.get('sample', False)
    if sample:
        content = export_json_file_sample()
        filename = "toolbox-import-example.json"
        response = make_response(content)
        response.headers['Content-Type'] = 'Content-Type: text/plain; charset=UTF-8'
        response.headers["Content-Disposition"] = "attachment; filename=" + filename
        return response

    # process the import file
    #if request.method == 'POST':
    #    files = request.files
    #    #flash("Importing file {}".format(form.jsonfile))
    #    current_app.logger.debug("Importing inventory file: {}".format(files))
    #form = JsonFileImportForm()        
    #if form.validate_on_submit():
    #    files = request.files
    #    flash("Importing file {}".format(form.jsonfile))
    #    current_app.logger.debug("Importing inventory file: {}".format(files))
    #    return redirect(url_for('inventory.index'))

    #return render_template('inventory/manage_import_export.html', form=form)

