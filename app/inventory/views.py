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
from app.inventory.forms import (
    NewDeviceForm, 
    NewSiteForm, 
    PingForm,
    SnmpForm
)

from app.device_tasks import (
    ping_device,
    snmp_device,
    task_status
)

from app.decorators import admin_required
from app.email import send_email
from app.models import EditableHTML, Role, User

from app.cli import (inventory_all_devices, inventory_all_sites,
                    inventory_device_details, inventory_device_delete,
                    inventory_site_details, inventory_site_delete,
                    inventory_device_add, inventory_site_add)

import json

inventory = Blueprint('inventory', __name__)


@inventory.route('/')
@login_required
def index():
    """Inventory dashboard page."""
    devices = inventory_all_devices()
    return render_template('inventory/index.html',
                            devices=devices
    )


## Devices
@inventory.route('/devices')
@login_required
def devices():
    """Inventory dashboard page."""
    devices = inventory_all_devices()
    return render_template('inventory/devices.html',
                            devices=devices
    )


@inventory.route('/new-device', methods=['GET', 'POST'])
@login_required
@admin_required
def new_device():
    """Create a new device."""
    form = NewDeviceForm()
    if form.validate_on_submit():
        device = {
            "hostname": form.hostname.data.lower(),
            "management_ip": form.management_ip.data,
            "siteid": form.site_id.data.upper()
        }
        inventory_device_add(device)
        flash('Device {} has been successfully created'.format(device["hostname"]),
              'form-success')
    return render_template('inventory/new_device.html', form=form)


@inventory.route('/device/<string:device_id>')
@inventory.route('/device/<string:device_id>/info')
@login_required
def device_info(device_id):
    """View site details."""
    device = inventory_device_details(device_id)
    if device is None:
        abort(404)
    return render_template('inventory/manage_device.html', device=device)


@inventory.route('/device/<string:device_id>/delete')
@login_required
@admin_required
def delete_device_request(device_id):
    """Request deletion of a site."""
    device = inventory_device_details(device_id)
    if device is None:
        abort(404)
    return render_template('inventory/manage_device.html', device=device)


@inventory.route('/device/<string:device_id>/_delete')
@login_required
@admin_required
def delete_device(device_id):
    rc = inventory_device_delete(device_id)
    if rc:
        flash('Successfully deleted device {}.'.format(device_id), 'success')
    else:
        flash('Failed to delete device {}.'.format(device_id), 'error')
    return redirect(url_for('inventory.devices'))


@inventory.route('/device/tools/<string:device_id>')
@inventory.route('/device/<string:device_id>/tools')
@login_required
def device_tools(device_id):
    """View site details."""
    device = inventory_device_details(device_id)
    if device is None:
        abort(404)
    return render_template('inventory/device_tools.html', device=device)


@inventory.route('/device/tools/<string:device_id>/ping', methods=['GET', 'POST'])
@inventory.route('/device/<string:device_id>/tools/ping', methods=['GET', 'POST'])
@login_required
def device_tools_ping(device_id):
    form = PingForm()
    device = inventory_device_details(device_id)
    job = None
    if device is None:
        abort(404)
    if form.validate_on_submit():
        job = json.loads(ping_device(device_id)[0].data)
    return render_template('inventory/device_tools.html', device=device, form=form, job=job)


@inventory.route('/device/tools/<string:device_id>/snmp', methods=['GET', 'POST'])
@inventory.route('/device/<string:device_id>/tools/snmp', methods=['GET', 'POST'])
@login_required
def device_tools_snmp(device_id):
    form = SnmpForm()
    device = inventory_device_details(device_id)
    job = None
    if device is None:
        abort(404)
    if form.validate_on_submit():
        job = json.loads(snmp_device(device_id, form.community.data, form.oid.data)[0].data)
    return render_template('inventory/device_tools.html', device=device, form=form, job=job)





## Sites
@inventory.route('/sites')
@login_required
def sites():
    """Inventory dashboard page."""
    sites = inventory_all_sites()
    return render_template('inventory/sites.html',
                            sites=sites
    )


@inventory.route('/new-site', methods=['GET', 'POST'])
@login_required
@admin_required
def new_site():
    """Create a new site."""
    form = NewSiteForm()
    if form.validate_on_submit():
        site = {
            "siteid": form.site_id.data.upper(),
            "city": form.city.data,
            "country": form.country.data,
            "region": form.region.data.upper()
        }
        inventory_site_add(site)
        flash('Site {} has been successfully created'.format(site["siteid"]),
              'form-success')
    return render_template('inventory/new_site.html', form=form)


@inventory.route('/site/<string:site_id>')
@inventory.route('/site/<string:site_id>/info')
@login_required
def site_info(site_id):
    """View site details."""
    site = inventory_site_details(site_id)
    if site is None:
        abort(404)
    return render_template('inventory/manage_site.html', site=site)


@inventory.route('/site/<string:site_id>/delete')
@login_required
@admin_required
def delete_site_request(site_id):
    """Request deletion of a site."""
    site = inventory_site_details(site_id)
    if site is None:
        abort(404)
    return render_template('inventory/manage_site.html', site=site)


@inventory.route('/site/<string:site_id>/_delete')
@login_required
@admin_required
def delete_site(site_id):
    rc = inventory_site_delete(site_id)
    if rc:
        flash('Successfully deleted site {}.'.format(site_id), 'success')
    else:
        flash('Failed to delete site {}.'.format(site_id), 'error')
    return redirect(url_for('inventory.sites'))






# TASKS:
@inventory.route('/tasks/<task_id>', methods=['GET'])
@login_required
def get_status(task_id):
    rc = task_status(task_id)
    return rc


