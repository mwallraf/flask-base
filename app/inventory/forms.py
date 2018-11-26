from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
    IPAddress
)
from app.cli import inventory_device_details, inventory_site_details


class NewDeviceForm(Form):
    hostname = StringField(
        'Hostname', validators=[InputRequired(),
                                  Length(1, 64)])
    management_ip = StringField(
        'Management IP', validators=[InputRequired(),
                                  Length(1, 64),
                                  IPAddress(ipv4=True, message="The management IP does not seem to be a valid IPv4 address")])
    site_id = StringField(
        'Site ID', validators=[InputRequired(),
                                  Length(6)])

    def validate_hostname(self, field):
        if inventory_device_details(field.data):
            raise ValidationError('This device already exists.')

    def validate_site_id(self, field):
        if not inventory_site_details(field.data.upper()):
            raise ValidationError('The Site ID does not exist, make sure you create it first.')

    submit = SubmitField('Add')



class NewSiteForm(Form):
    site_id = StringField(
        'Site ID', validators=[InputRequired(),
                                  Length(6)])
    city = StringField(
        'City', validators=[InputRequired(),
                                  Length(1, 64)])
    country = StringField(
        'Country', validators=[InputRequired(),
                                  Length(1, 64)])
    region = StringField(
        'Region', validators=[InputRequired(),
                                  Length(1, 64)])

    def validate_site_id(self, field):
        if inventory_site_details(field.data.upper()):
            raise ValidationError('The Site ID already exists.')

    submit = SubmitField('Add')


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


