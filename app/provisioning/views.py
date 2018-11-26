from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify
)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db
from app.provisioning.forms import NewTemplateForm

from app.decorators import admin_required
from app.email import send_email
from app.models import ProvisioningTemplate


provisioning = Blueprint('provisioning', __name__)


@provisioning.route('/')
@login_required
def index():
    """Provisioning dashboard page."""
    return render_template('provisioning/index.html')


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
def new_temlate():
    """Create a new provisioning template."""
    template_options = [
        "description", 
        "hardware", 
        "software", 
        "created_by",
        "created"    
    ]
    form = NewTemplateForm()
    if form.validate_on_submit():
        template = ProvisioningTemplate(
            name=form.name.data)
        db.session.add(template)
        db.session.commit()
        flash('Template {} successfully created'.format(template.name),
              'form-success')
    return render_template('provisioning/new_template.html', 
        form=form,
        template_options=template_options)


@provisioning.route('/manage_template/<int:template_id>')
@provisioning.route('/manage_template/<int:template_id>/info')
@login_required
def manage_template(template_id):
    template = ProvisioningTemplate.query.filter_by(id=template_id).first()
    return render_template(
        'provisioning/manage_template.html',
        template=template
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




@provisioning.route('/keywords')
@login_required
@admin_required
def keywords():
    """Provisioning dashboard page."""
    return render_template('provisioning/index.html')







# from flask import current_app as app, jsonify, render_template, render_template_string, request
# from flask_login import current_user
# from eNMS.provisioning.helpers import get_template_vars, get_all_snippets
# from eNMS.provisioning import bp
# from eNMS.base.helpers import get
# 
# 
# @get(bp, '/test', 'Provisioning Section')
# def test():
# 
#     snippets = get_all_snippets(bp)
#     print(snippets)
# 
#     tpl_source = snippets['snippets/test.j2']['template']
#     tpl_vars = { x: 'blablabla' for x in snippets['snippets/test.j2']['vars'] }
# 
#     rendering_result = render_template_string(tpl_source, **tpl_vars)
# 
#     return render_template(
#         'test.html',
#         rendering_result=rendering_result
#     )
# 
# # -----
# 
# @get(bp, '/', 'Provisioning Section')
# def provisioning():
# 
#     snippets = get_all_snippets(bp)
#     #print(snippets)
# 
#     tpl_source = snippets['snippets/test.j2']['template']
#     tpl_vars = { x: 'blablabla' for x in snippets['snippets/test.j2']['vars'] }
# 
#     rendering_result = render_snippet(tpl_source, **tpl_vars)
# 
#     return render_template(
#         'provisioning.html',
#         snippets=snippets,
#         snippet_vars=snippets['snippets/test.j2']['vars'],
#         rendering_result=rendering_result
#     )
# 
# 
# @get(bp, '/', 'Provisioning Section')
# def render_snippet(snippet_src, **kwargs):
#     rendering_result = render_template_string(snippet_src, **kwargs)
#     return rendering_result
