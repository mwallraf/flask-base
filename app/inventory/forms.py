from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
    HiddenField,
    SelectField,
    FileField
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
    IPAddress,
    regexp
)
from config import Config
from flask import current_app
from .. import db
from app.models import InventoryCustomer, InventorySite, InventoryDevice
from app.cli import inventory_device_details, inventory_site_details
import json



def NewDeviceForm(*args, **kwargs):
    class DeviceForm(Form):

        hostname = StringField(
            'Hostname', validators=[InputRequired(),
                                      Length(1, 64)])
        managementip = StringField(
            'Management IP', validators=[IPAddress()])

        domain = StringField(
            'Domain name', validators=[InputRequired(), Length(1, 100)])

        function = SelectField(
                'Device function',
                validators=[InputRequired()],
                default="access_switch",
                choices=[
                    ('switch_access', 'Access Switch'), 
                    ('switch_core', 'Core Switch'), 
                    ('wlan_wlc', 'Wireless LAN Controller'), 
                    ('wlan_ap', 'Access Point'), 
                    ('voice_gateway', 'Voice Gateway')
                ]
            )

        site_id = QuerySelectField(
            'Site',
            validators=[InputRequired()],
            get_label='siteid',
            query_factory=lambda: db.session.query(InventorySite).order_by('siteid'))

        submit = SubmitField('Add')


        def validate_hostname(self, field):
            # if the form is updated then don't check for duplicate ID if it didn't change
            if self.__dict__.get('old_hostname') and self.__dict__.get('old_hostname').data == field.data:
                return True
            if InventoryDevice.query.filter_by(hostname=field.data).first():
                raise ValidationError('A device with this hostname already exists.')

        def validate_managementip(self, field):
            # if the form is updated then don't check for duplicate ID if it didn't change
            if (not field.data) or (self.__dict__.get('old_managementip') and self.__dict__.get('old_managementip').data == field.data):
                return True
            if InventoryDevice.query.filter_by(managementip=field.data).first():
                raise ValidationError('A device with this management IP already exists.')

        def get_options(self):
            """
            Returns possible options inside the options json field.
            Field names are prepended with "option_"
            """
            return [ "option_{}".format(o) for o in InventoryDevice.get_options()]

        def compress_options(self):
            """
            returns a json of options to be stored in DB,
            removes option_ from each value
            """
            options = {}
            for option in self.get_options():
                options[option.replace("option_", "")] = self.data.get(option, "")
            return json.dumps(options)

        def set_submit_value(self, label):
            self.submit.label.text = label


    """
    Create dynamic fields fore each possible options inside the options json field.
    Field names are prepended with "option_"
    """
    for key in InventoryDevice.get_options():
        setattr(DeviceForm, "option_{}".format(key), StringField(key))

    # this is used to disable validation in case the form is used for update instead of add
    if kwargs.get("old_hostname", False):
        setattr(DeviceForm, "old_hostname", HiddenField("old_hostname", default=kwargs["old_hostname"]))

    # this is used to disable validation in case the form is used for update instead of add
    if kwargs.get("old_managementip", False):
        setattr(DeviceForm, "old_managementip", HiddenField("old_managementip", default=kwargs["old_managementip"]))

    return DeviceForm(*args, **kwargs)




def NewSiteForm(*args, **kwargs):
    class SiteForm(Form):

        siteid = StringField(
            'Site ID', validators=[InputRequired(),
                                      Length(6)])
        name = StringField(
            'Site name', validators=[])
        address = StringField(
            'Address', validators=[])
        city = StringField(
            'City', validators=[InputRequired(),
                                      Length(1, 64)])
        country = StringField(
            'Country', validators=[InputRequired(),
                                      Length(1, 64)])
        region = SelectField(
                'Region',
                validators=[InputRequired()],
                choices=[(region, region.upper()) for region in Config.REGIONS]
            )

        customer_id = QuerySelectField(
            'Customer',
            validators=[InputRequired()],
            get_label='name',
            query_factory=lambda: db.session.query(InventoryCustomer).order_by('name'))

        def validate_siteid(self, field):
            # if the form is updated then don't check for duplicate ID if it didn't change
            if self.__dict__.get('old_siteid') and self.__dict__.get('old_siteid').data == field.data:
                return True
            if InventorySite.query.filter_by(siteid=field.data).first():
                raise ValidationError('The Site ID already exists.')


        submit = SubmitField('Add')

        def get_options(self):
            """
            Returns possible options inside the options json field.
            Field names are prepended with "option_"
            """
            return [ "option_{}".format(o) for o in InventorySite.get_options()]

        def compress_options(self):
            """
            returns a json of options to be stored in DB,
            removes option_ from each value
            """
            options = {}
            for option in self.get_options():
                options[option.replace("option_", "")] = self.data.get(option, "")
            return json.dumps(options)

        def set_submit_value(self, label):
            self.submit.label.text = label


    """
    Create dynamic fields fore each possible options inside the options json field.
    Field names are prepended with "option_"
    """
    for key in InventorySite.get_options():
        setattr(SiteForm, "option_{}".format(key), StringField(key))

    # this is used to disable validation in case the form is used for update instead of add
    if kwargs.get("old_siteid", False):
        setattr(SiteForm, "old_siteid", HiddenField("old_siteid", default=kwargs["old_siteid"]))

    return SiteForm(*args, **kwargs)



### DEVICE TOOLS FORMS ###

class PingForm(Form):
    submit = SubmitField('Start ping')


class SnmpForm(Form):
    community = StringField(
        'SNMP Community', validators=[InputRequired(),
                                  Length(1, 64)],
                                    default="public")
    oid = StringField(
        'SNMP OID', validators=[Length(1, 64)],
                                    default=".1.3.6.1.2.1.1")

    submit = SubmitField('Start snmp walk')


