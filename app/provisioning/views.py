from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    current_app,
    render_template_string,
    make_response
)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db
from app.provisioning.forms import (
    NewTemplateForm,
    NewProvisioningForm,
    NewKeywordForm,
    ConnectionForm,
    DownloadForm
)

from app.decorators import admin_required
from app.email import send_email
from app.models import (
    ProvisioningTemplate,
    ProvisioningKeyword
)

from app.device_tasks import send_config_to_device

from wtforms.compat import iteritems

from app.provisioning.helpers import get_template_vars

import json
import copy

provisioning = Blueprint('provisioning', __name__)

@provisioning.route('/')
@login_required
def index():
    """Provisioning dashboard page."""
    return render_template('provisioning/index.html')



## TEMPLATES
@provisioning.route('/templates')
@login_required
def templates():
    """Provisioning dashboard page."""
    templates = ProvisioningTemplate.query.all()
    return render_template(
        'provisioning/templates.html',
        templates=templates
    )


@provisioning.route('/new-template', methods=['GET', 'POST'])
@login_required
@admin_required
def new_template():
    """Create a new provisioning template."""
    form = NewTemplateForm()
    keywords = ProvisioningKeyword.query.all()

    if form.validate_on_submit():
        template = ProvisioningTemplate(
            name=form.name.data,
            template=form.template.data,
            options=form.compress_options(),
            enabled=request.form.get("enabled", False)
            )
        db.session.add(template)
        db.session.commit()
        flash('Template {} successfully created'.format(template.name),
              'form-success')
        return redirect(url_for('provisioning.templates'))

    return render_template('provisioning/new_template.html', 
        form=form,
        keywords=keywords
        )


@provisioning.route('/manage_template/<int:template_id>')
@provisioning.route('/manage_template/<int:template_id>/info')
@login_required
def manage_template(template_id):
    template = ProvisioningTemplate.query.filter_by(id=template_id).first()
    return render_template(
        'provisioning/manage_template.html',
        template=template
    )


@provisioning.route('/template/<int:template_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_template(template_id):
    """Change a template's details."""
    template = ProvisioningTemplate.query.filter_by(id=template_id).first()
    if template is None:
        abort(404)

    form = NewTemplateForm(obj=template, **template.extract_options())
    form.set_submit_value("Update")

    keywords = ProvisioningKeyword.query.all()

    if form.validate_on_submit():
        template.options = form.compress_options()
        template.name = form.name.data
        template.template = form.template.data
        template.enabled = request.form.get("enabled", False)

        db.session.add(template)
        db.session.commit()
        flash('Template {} successfully updated.'.format(template.name), 'form-success')

    return render_template(
        'provisioning/manage_template.html',
        template=template,
        keywords=keywords,
        form=form
    )



@provisioning.route('/template/<int:template_id>/delete')
@login_required
@admin_required
def delete_template_request(template_id):
    """Request deletion of a template."""
    template = ProvisioningTemplate.query.filter_by(id=template_id).first()
    if template is None:
        abort(404)
    return render_template('provisioning/manage_template.html', template=template)


@provisioning.route('/template/<int:template_id>/_delete')
@login_required
@admin_required
def delete_template(template_id):
    """Delete a template."""
    template = ProvisioningTemplate.query.filter_by(id=template_id).first()
    db.session.delete(template)
    db.session.commit()
    flash('Successfully deleted template {}.'.format(template.name), 'success')
    return redirect(url_for('provisioning.templates'))



@provisioning.route('/template/<int:template_id>/config', methods=['GET', 'POST'])
@login_required
def generate_configuration_template(template_id):
    """Generate configuration based on a template
    """
    template = ProvisioningTemplate.query.filter_by(id=template_id).first()
    if template is None:
        abort(404)

    tpl_vars = get_template_vars(template.name)
    known_keywords = { kw.keyword:kw.value for kw in ProvisioningKeyword.query.all() if kw.value }
    form = NewProvisioningForm(template_vars=tpl_vars, **known_keywords)

    if form.validate_on_submit():
        rendering_result = render_template_string(template.template, **form.data)

        return render_template('provisioning/manage_template.html', 
            template=template,
            rendered_template=rendering_result,
            form=form,
        )
    return render_template('provisioning/manage_template.html', 
        template=template,
        form=form)



@provisioning.route('/provision/<int:template_id>', methods=['GET', 'POST'])
@login_required
def provision_template(template_id):
    template = ProvisioningTemplate.query.filter_by(id=template_id).first()
    if template is None:
        abort(404)

    tpl_vars = get_template_vars(template.name)

    # all_keywords is used 
    all_keywords = [ kw for kw in ProvisioningKeyword.query.all() if kw.keyword in tpl_vars ]

    #
    known_keywords = { kw.keyword:kw.value for kw in all_keywords if kw.value }
    #form = NewProvisioningForm(template_vars=tpl_vars, all_keywords=all_keywords, **known_keywords)
    form = NewProvisioningForm(template_vars=tpl_vars, all_keywords=all_keywords)

    if form.validate_on_submit():
        rendering_result = render_template_string(template.template, **form.data)

        return render_template('provisioning/provision_template.html', 
            template=template,
            rendered_template=rendering_result,
            form=form,
            connection_form=ConnectionForm(),
            downloadform=DownloadForm()
        )

    return render_template(
        'provisioning/provision_template.html',
        template=template,
        form=form,
        connection_form=ConnectionForm(),
        downloadform=DownloadForm()
    )





## KEYWORDS
@provisioning.route('/keywords')
@login_required
def keywords():
    keywords = ProvisioningKeyword.query.all()
    return render_template(
        'provisioning/keywords.html',
        keywords=keywords
    )

@provisioning.route('/manage_keyword/<int:keyword_id>')
@provisioning.route('/manage_keyword/<int:keyword_id>/info')
@login_required
def manage_keyword(keyword_id):
    keyword = ProvisioningKeyword.query.filter_by(id=keyword_id).first()
    return render_template(
        'provisioning/manage_keyword.html',
        keyword=keyword
    )


    order = db.Column(db.Integer)


@provisioning.route('/new-keyword', methods=['GET', 'POST'])
@login_required
@admin_required
def new_keyword():
    """Create a new keyword."""
    form = NewKeywordForm()

    if form.validate_on_submit():
        keyword = ProvisioningKeyword(
            keyword=form.keyword.data,
            value=form.value.data,
            default_value=form.default_value.data,
            description=form.description.data,
            type=form.type.data,
            options=form.compress_options(),
            required=request.form.get("required", False),
            regex=form.regex.data,
            widget=form.widget.data,
            order=ProvisioningKeyword().next_order()
            )
        db.session.add(keyword)
        db.session.commit()
        flash('Keyword {} successfully created'.format(keyword.keyword),
              'form-success')
        return redirect(url_for('provisioning.keywords'))

    return render_template('provisioning/new_keyword.html', 
        form=form
        )


@provisioning.route('/keyword/<int:keyword_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_keyword(keyword_id):
    """Change a template's details."""
    keyword = ProvisioningKeyword.query.filter_by(id=keyword_id).first()
    if keyword is None:
        abort(404)

    form = NewKeywordForm(obj=keyword, **keyword.extract_options())
    form.set_submit_value("Update")

    if form.validate_on_submit():
        keyword.keyword = form.keyword.data
        keyword.value = form.value.data
        keyword.default_value = form.default_value.data
        keyword.description = form.description.data
        keyword.type = form.type.data
        keyword.options = form.compress_options()
        keyword.required = request.form.get("required", False)
        keyword.regex = form.regex.data
        keyword.widget = form.widget.data

        db.session.add(keyword)
        db.session.commit()
        flash('Keyword {} successfully updated.'.format(keyword.keyword), 'form-success')

    return render_template(
        'provisioning/manage_keyword.html',
        keyword=keyword,
        form=form
    )

@provisioning.route('/keyword/<int:keyword_id>/delete')
@login_required
@admin_required
def delete_keyword_request(keyword_id):
    """Request deletion of a template."""
    keyword = ProvisioningKeyword.query.filter_by(id=keyword_id).first()
    if keyword is None:
        abort(404)
    return render_template('provisioning/manage_keyword.html', keyword=keyword)


@provisioning.route('/keyword/<int:keyword_id>/_delete')
@login_required
@admin_required
def delete_keyword(keyword_id):
    """Delete a template."""
    keyword = ProvisioningKeyword.query.filter_by(id=keyword_id).first()
    db.session.delete(keyword)
    db.session.commit()
    flash('Successfully deleted keyword {}.'.format(keyword.keyword), 'success')
    return redirect(url_for('provisioning.keywords'))


# AJAX CALLS
@provisioning.route('/tasks/sendtodevice', methods=["POST"])
def send_to_device():
    connection_details = {
        "hostname": request.form["hostname"],
        "username": request.form["username"],
        "password": request.form["password"],
        "transport": request.form["transport"],
        "driver": request.form["driver"],
        "config": request.form["config"]
    }
    rc = send_config_to_device(connection_details)
    #current_app.logger.debug("form.config.data = {}".format(request.form["config"]))
    return rc


