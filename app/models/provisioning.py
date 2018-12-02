from .. import db
import json
from datetime import datetime
from flask_login import current_user
from app.models.user import User
import json
from sqlalchemy import desc


class BaseModelWithOptions(db.Model):

    __abstract__ = True


    def extract_options(self, prepend="option_"):
        """
        Adds "option_" to each individual option and returns
        a dict
        """
        opts = {}
        try:
            opts = json.loads(self.options)
        except:
            pass
        return { "{}{}".format(prepend, key): opts.get(key, "") for key in self.get_options() }


    @classmethod
    def get_options(cls):
        """
        Returns the individual options that can be used in the options field
        In order that should be displayed in HTML
        """
        return []

    @property
    def is_visible(self):
        return not (hasattr(self, 'hidden') and self.hidden)

    @property
    def is_enabled(self):
        return not (hasattr(self, 'enabled') and self.enabled)

    @property
    def is_required(self):
        return not (hasattr(self, 'required') and self.required)

    def get_option(self, option):
        """
        Return the value of the option if exists,
            otherwise retun empty string
        """
        rc = ""
        try:
            rc = json.loads(self.options).get(option, "")
        except:
            pass
        return rc



class ProvisioningKeyword(BaseModelWithOptions):
    """
    Store pre-defined keywords that can be used in templates.

    Keywords that are known in the DB can influence forms
    by defining the widget type, default values, etc

    Keywords not known in the DB will be considered as regular
    String fields in a form.

    keyword = keyword name
    value = (optional) the value of the keyword
    default_value = use this value by default if value is empty
    type = int|ip|ip_cidr|string|boolean
    description = Description of the keyword, visible in GUI
    example = example value
    required
    order = order to display in GUI
    """
    __tablename__ = 'provisioning_keyword'

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), unique=True)
    type = db.Column(db.String(40))
    value = db.Column(db.String)
    default_value = db.Column(db.String)
    description = db.Column(db.String)
    regex = db.Column(db.String)
    required = db.Column(db.Boolean)
    widget = db.Column(db.String)
    enabled = db.Column(db.Boolean, default=True)
    visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=lambda: current_user.get_id())
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    order = db.Column(db.Integer, default=0)
    options = db.Column(db.Text, default=json.dumps({
        "validators": ""
    }))

    def next_order(self):
        """
        Returns the next order index
        """
        kw = ProvisioningKeyword.query.filter_by().order_by(desc("order")).first()
        if kw:
            return int(kw.order) + 1
        else:
            return 1

    @classmethod
    def get_options(cls):
        """
        Returns the individual options that can be used in the options field
        In order that should be displayed in HTML
        """
        return ["validators"]


    def __repr__(self):
        return "<Keyword \'{}\'>".format(self.keyword)



class ProvisioningTemplate(BaseModelWithOptions):
    """
    name = short template name
    template = the actual template (JINJA format)
    enabled = if it should be used in production
    options = dict of extra options
    {
        "description": "",
        "hardware": "",
        "software": ""
    }
    """
    __tablename__ = 'provisioning_template'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    template = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=lambda: current_user.get_id())
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=lambda: current_user.get_id(), onupdate=lambda: current_user.get_id())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    updated_by = db.relationship("User", foreign_keys=[updated_by_id])

    options = db.Column(db.Text, default=json.dumps({
                    "description": "", 
                    "hardware": "", 
                    "software": ""
    }))
    enabled = db.Column(db.Boolean)

    @classmethod
    def get_options(cls):
        """
        Returns the individual options that can be used in the options field
        In order that should be displayed in HTML
        """
        return ["description", "hardware", "software"]


    def __repr__(self):
        return "<Template \'{}\'>".format(self.name)

