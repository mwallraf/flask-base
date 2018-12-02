from flask_wtf import Form
from wtforms import ValidationError
from wtforms.fields import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
    SelectField,
    HiddenField
)
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
    IPAddress,
    Regexp
)
import json
from app.models import (
    ProvisioningTemplate,
    ProvisioningKeyword
    )
import re


class DownloadForm(Form):
    """
        Empty form, for AJAX requests
    """
    pass


def NewProvisioningForm(*args, **kwargs):

    class ProvisioningForm(Form):
        submit = SubmitField('Generate config')

    """
    Create dynamic fields fore each keyword found in "template_vars"
    """
    all_keys = kwargs.get("all_keywords", [])

    for key in kwargs.get("template_vars", []):
        key_found = next(filter(lambda x: x.keyword == key, all_keys), None)
        fld = None
        validators = []
        default_value = None
        if key_found:
            if key_found.regex:
                validators.append(Regexp(key_found.regex, message="Field must match regex '{}'".format(key_found.regex)))
            if key_found.required:
                validators.append(InputRequired())
            if key_found.default_value:
                default_value = key_found.default_value
            if key_found.value:
                default_value = key_found.value
            if key_found.widget == "stringfield":
                fld = StringField(key, validators=validators, default=default_value)
        if not fld:
            fld = StringField(key)
        setattr(ProvisioningForm, "{}".format(key), fld)

    return ProvisioningForm(*args, **kwargs)



def NewTemplateForm(*args, **kwargs):
    """
    Form to manage create/update Templates.
    This is a dynamic form:
       fields in the table.options are stored in JSON
       but will be displayed as seperate text fields
    """
    class TemplateForm(Form):
        enabled = BooleanField('Enable for production', default=True)
        name = StringField(
            'name', validators=[InputRequired(),
                                      Length(1, 64)]
            )
        template = TextAreaField('template content',
            validators=[InputRequired()]
            )
        submit = SubmitField('Create')

        def get_options(self):
            """
            Returns possible options inside the options json field.
            Field names are prepended with "option_"
            """
            return [ "option_{}".format(o) for o in ProvisioningTemplate.get_options()]

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
    for key in ProvisioningTemplate.get_options():
        setattr(TemplateForm, "option_{}".format(key), StringField(key))

    return TemplateForm(*args, **kwargs)


class ConnectionForm(Form):
    hostname = StringField('Hostname or IP address', validators=[InputRequired(),
                                      Length(1, 64),
                                      ])
    username = StringField('Username', validators=[InputRequired(),
                                      Length(1, 64),
                                      ])
    password = PasswordField('Password', validators=[InputRequired(),
                                      Length(1, 64),
                                      ])
    driver = SelectField(
            'Device Type',
            validators=[InputRequired()],
            default="cisco_ios",
            choices=[('cisco_ios', 'Cisco switch or router'), ('cisco_wls', 'Cisco WLC'), ('hp_procurve', 'HP Procurve')]
        )
    transport = SelectField(
            'Transport method',
            validators=[InputRequired()],
            default="ssh",
            choices=[('ssh', 'SSH'), ('telnet', 'Telnet')]
        )
    config = HiddenField()


def NewKeywordForm(*args, **kwargs):
    """
    Form to manage create/update keywords.
    This is a dynamic form:
       fields in the table.options are stored in JSON
       but will be displayed as seperate text fields
    """
    class KeywordForm(Form):
        keyword = StringField(
            'Keyword', validators=[InputRequired(),
                                      Length(1, 64),
                                      ]
            )

        type = SelectField(
            'Keyword type',
            validators=[InputRequired()],
            choices=[('string', 'String'), ('int', 'integer'), ('ip', 'IP Address'), ('ip_cidr', 'IP Address/Mask'), ('boolean', "Boolean")]
        )

        value = StringField('Value', validators=[])
        default_value = StringField('Default value', validators=[])
        description = StringField('Description', validators=[])
        regex = StringField('Regular Expression', validators=[])

        widget = SelectField(
            'Widget type',
            validators=[],
            choices=[('stringfield', 'StringField'), ('checkbox', 'Checkbox')]
        )

        required = BooleanField('Required', default=True)


        submit = SubmitField('Create')


        def validate_keyword(self, field):
            if not field.data == field.data.upper():
                raise ValidationError('Keywords should be in upper case.')

        def validate_regex(self, field):
            try:
                re.compile(field.data)
            except:
                raise ValidationError('Invalid regualar expression - check syntax.')


        def get_options(self):
            """
            Returns possible options inside the options json field.
            Field names are prepended with "option_"
            """
            return [ "option_{}".format(o) for o in ProvisioningKeyword.get_options()]

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
    for key in ProvisioningKeyword.get_options():
        setattr(KeywordForm, "option_{}".format(key), StringField(key))

    return KeywordForm(*args, **kwargs)
