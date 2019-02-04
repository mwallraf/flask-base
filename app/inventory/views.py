from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    current_app
)
from flask_login import current_user, login_required
from flask_rq import get_queue

from werkzeug.utils import secure_filename

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
from app.models import EditableHTML, Role, User, InventorySite, InventoryDevice, InventoryPool

from app.cli import (inventory_device_details, inventory_device_delete)

import json

inventory = Blueprint('inventory', __name__)


@inventory.route('/')
@login_required
def index():
    """Inventory dashboard page."""
    return render_template('inventory/index.html')


## Devices
@inventory.route('/devices')
@login_required
def devices():
    """Inventory dashboard page."""
    devices = InventoryDevice.query.all()
    return render_template('inventory/devices.html',
                            devices=devices
    )


## AJAX calls client

@inventory.route('/devices/all', methods=['GET'])
@login_required
def get_all_device_records():
    """
      Returns a json format of all tacacs clients
      This function should be used by AJAX call for populating the datatable
    """
    data = [ x.serialize_json(jsonformat=False, allownull=False, showid=True) for x in InventoryDevice.query.all() ]
    #print("get_all_client_records data = {}".format(data))
    return jsonify({ "data": data } )




@inventory.route('/new-device', methods=['GET', 'POST'])
@login_required
@admin_required
def new_device():
    """Create a new device."""
    form = NewDeviceForm()
    if form.validate_on_submit():
        device = InventoryDevice(
            hostname=form.hostname.data.lower(),
            domain=form.domain.data,
            managementip=form.managementip.data,
            function=form.function.data,
            site=form.site_id.data
        )
        db.session.add(device)
        db.session.commit()
        flash('Device {} has been successfully created'.format(device.hostname),
              'form-success')
        return redirect(url_for('inventory.devices'))

    return render_template('inventory/new_device.html', form=form)


@inventory.route('/device/<int:device_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_device(device_id):
    """Update site details."""
    device = InventoryDevice.query.filter_by(id=device_id).first()
    if device is None:
        abort(404)

    form = NewDeviceForm(obj=device, old_hostname=device.hostname, old_managementip=device.managementip, **device.extract_options())
    form.set_submit_value("Update")

    if form.validate_on_submit():
        device.hostname = form.hostname.data.lower()
        device.domain = form.domain.data.lower()
        device.managementip = form.managementip.data
        device.function = form.function.data
        device.site = form.site_id.data
        db.session.add(device)
        db.session.commit()

        flash('Device {} has been successfully created'.format(device.hostname),
              'form-success')
        return redirect(url_for('inventory.devices'))

    return render_template('inventory/manage_device.html', device=device, form=form)




@inventory.route('/device/<string:device_id>')
@inventory.route('/device/<string:device_id>/info')
@login_required
def device_info(device_id):
    """View site details."""
    device = InventoryDevice.query.filter_by(id=device_id).first()
    if device is None:
        abort(404)
    return render_template('inventory/manage_device.html', device=device)


@inventory.route('/device/<string:device_id>/delete')
@login_required
@admin_required
def delete_device_request(device_id):
    """Request deletion of a site."""
    device = InventoryDevice.query.filter_by(id=device_id).first()
    if device is None:
        abort(404)
    return render_template('inventory/manage_device.html', device=device)


@inventory.route('/device/<string:device_id>/_delete')
@login_required
@admin_required
def delete_device(device_id):
    device = InventoryDevice.query.filter_by(id=device_id).first()
    if device:
        flash('Successfully deleted device {}.'.format(device.hostname), 'success')
        db.session.delete(device)
        db.session.commit()
    else:
        flash('Failed to delete device {}.'.format(device.hostname), 'error')
    return redirect(url_for('inventory.devices'))


@inventory.route('/device/tools/<string:device_id>')
@inventory.route('/device/<string:device_id>/tools')
@login_required
def device_tools(device_id):
    """View site details."""
    device = InventoryDevice.query.filter_by(id=device_id).first()
    if device is None:
        abort(404)
    return render_template('inventory/device_tools.html', device=device)


@inventory.route('/device/tools/<string:device_id>/ping', methods=['GET', 'POST'])
@inventory.route('/device/<string:device_id>/tools/ping', methods=['GET', 'POST'])
@login_required
def device_tools_ping(device_id):
    form = PingForm()
    device = InventoryDevice.query.filter_by(id=device_id).first()
    job = None
    if device is None:
        abort(404)
    if form.validate_on_submit():
        job = json.loads(ping_device(device.hostname)[0].data)
    return render_template('inventory/device_tools.html', device=device, form=form, job=job)


@inventory.route('/device/tools/<string:device_id>/snmp', methods=['GET', 'POST'])
@inventory.route('/device/<string:device_id>/tools/snmp', methods=['GET', 'POST'])
@login_required
def device_tools_snmp(device_id):
    form = SnmpForm()
    device = InventoryDevice.query.filter_by(id=device_id).first()
    job = None
    if device is None:
        abort(404)
    if form.validate_on_submit():
        job = json.loads(snmp_device(device.hostname, form.community.data, form.oid.data)[0].data)
    return render_template('inventory/device_tools.html', device=device, form=form, job=job)




## Sites
@inventory.route('/sites')
@login_required
def sites():
    """Inventory dashboard page."""
    sites = InventorySite.query.all()
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
        site = InventorySite(
            siteid=form.siteid.data.upper(),
            name=form.name.data,
            address=form.address.data,
            city=form.city.data,
            country=form.country.data,
            region=form.region.data.upper(),
            customer=form.customer_id.data,
            options=form.compress_options()
        )
        db.session.add(site)
        db.session.commit()

        flash('Site {} has been successfully created'.format(site.siteid),
              'form-success')
        return redirect(url_for('inventory.sites'))

    return render_template('inventory/new_site.html', form=form)


@inventory.route('/site/<string:site_id>')
@inventory.route('/site/<string:site_id>/info')
@login_required
def site_info(site_id):
    """View site details."""
    site = InventorySite.query.filter_by(id=site_id).first()
    if site is None:
        abort(404)
    return render_template('inventory/manage_site.html', site=site)


@inventory.route('/site/<int:site_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_site(site_id):
    """Update site details."""
    site = InventorySite.query.filter_by(id=site_id).first()
    if site is None:
        abort(404)

    form = NewSiteForm(obj=site, old_siteid=site.siteid, **site.extract_options())
    form.set_submit_value("Update")

    if form.validate_on_submit():
        site.siteid = form.siteid.data.upper()
        site.name = form.name.data
        site.address = form.address.data
        site.city = form.city.data
        site.country = form.country.data
        site.region = form.region.data.upper()
        site.customer = form.customer_id.data
        site.options = form.compress_options()
        db.session.add(site)
        db.session.commit()

        flash('Site {} has been successfully created'.format(site.siteid),
              'form-success')
        return redirect(url_for('inventory.sites'))

    return render_template('inventory/manage_site.html', site=site, form=form)



@inventory.route('/site/<string:site_id>/delete')
@login_required
@admin_required
def delete_site_request(site_id):
    """Request deletion of a site."""
    site = InventorySite.query.filter_by(id=site_id).first()
    if site is None:
        abort(404)
    return render_template('inventory/manage_site.html', site=site)



@inventory.route('/site/<string:site_id>/_delete')
@login_required
@admin_required
def delete_site(site_id):
    site = InventorySite.query.filter_by(id=site_id).first()
    if site:
        db.session.delete(site)
        db.session.commit()
        flash('Successfully deleted site {}.'.format(site.siteid), 'success')
    else:
        flash('Failed to delete site {}.'.format(site.siteid), 'error')
    return redirect(url_for('inventory.sites'))




## Device Pools
@inventory.route('/pools')
@login_required
def pools():
    """Inventory pool dashboard page."""
    pools = InventoryPool.query.all()
    return render_template('inventory/pools.html',
                            pools=pools
    )

@inventory.route('/new-pool', methods=['GET', 'POST'])
@login_required
@admin_required
def new_pool():
    """Create a new device pool."""
    #form = NewSiteForm()
    #if form.validate_on_submit():
    #    site = InventorySite(
    #        siteid=form.siteid.data.upper(),
    #        name=form.name.data,
    #        address=form.address.data,
    #        city=form.city.data,
    #        country=form.country.data,
    #        region=form.region.data.upper(),
    #        customer=form.customer_id.data,
    #        options=form.compress_options()
    #    )
    #    db.session.add(site)
    #    db.session.commit()

    #    flash('Site {} has been successfully created'.format(site.siteid),
    #          'form-success')
    #    return redirect(url_for('inventory.sites'))

    #return render_template('inventory/new_site.html', form=form)
    pass


@inventory.route('/pool/<string:pool_id>')
@inventory.route('/pool/<string:pool_id>/info')
@login_required
def pool_info(pool_id):
    """View site details."""
    pool = InventoryPool.query.filter_by(id=pool_id).first()
    if InventoryPool is None:
        abort(404)
    #return render_template('inventory/manage_pool.html', pool=pool)
    pass



# TASKS:
@inventory.route('/tasks/<task_id>', methods=['GET'])
@login_required
def get_status(task_id):
    rc = task_status(task_id)
    return rc


