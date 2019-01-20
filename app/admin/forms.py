from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
    BooleanField,
    HiddenField,
    FileField
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
    Regexp
)

from app import db
from app.models import Role, User


class ChangeUserEmailForm(Form):
    email = EmailField(
        'New email', validators=[InputRequired(),
                                 Length(1, 64),
                                 Email()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangeAccountTypeForm(Form):
    role = QuerySelectField(
        'New account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    submit = SubmitField('Update role')


class UpdateUserForm(Form):
    first_name = StringField(
        'First name', validators=[InputRequired(),
                                  Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(),
                                 Length(1, 64)])
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])
    confirmed = BooleanField('User has been confirmed', default=False)
    submit = SubmitField('Update')


class InviteUserForm(Form):
    role = QuerySelectField(
        'Account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    first_name = StringField(
        'First name', validators=[InputRequired(),
                                  Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(),
                                 Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])
    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class NewUserForm(InviteUserForm):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])

    submit = SubmitField('Create')


class JsonFileImportForm(Form):
    jsonfile = FileField('Upload JSON', [ Regexp("^.*\.json$") ])
    submit = SubmitField('Import file')


class NewUsefulLinkForm(Form):
    name = StringField(
        'Name', validators=[InputRequired(),
                                  Length(1, 100)])
    url = StringField(
        'URL', validators=[InputRequired(),
                                  Length(1, 100)])
    title = StringField(
        'Title', validators=[InputRequired(),
                                  Length(1, 100)])
    short_descr = StringField(
        'Short Description', validators=[InputRequired(),
                                  Length(1, 100)])
    long_descr = StringField(
        'Long Description', validators=[])
    tooltip = StringField(
        'Tooltip', validators=[])
    img = StringField('Upload JPG')
    enabled = BooleanField('Visible', default=True)

    submit = SubmitField('Add link')


