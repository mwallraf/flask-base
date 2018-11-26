from flask_wtf import Form
from wtforms import ValidationError
from wtforms.fields import (
    BooleanField,
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
import json


template_options = [
    "description", 
    "hardware", 
    "software", 
    "created_by",
    "created"    
]


def NewTemplateForm(*args, **kwargs):
    """
    Dynamic form to handle the options field
    """
    class StaticForm(Form):
        name = StringField(
            'name', validators=[InputRequired(),
                                      Length(1, 64)])
        template = StringField('template content')
        enabled = BooleanField('Enable for production')
        submit = SubmitField('Create')

    for key in template_options:
        setattr(StaticForm, "option_{}".format(key), StringField(key))

    return StaticForm()
