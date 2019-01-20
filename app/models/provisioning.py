from .. import db
import json
from datetime import datetime
from flask_login import current_user
from app.models.user import User
from app.models.miscellaneous import BaseModelWithOptions
from sqlalchemy import desc
from flask import current_app


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

    @classmethod
    def sample_json(cls):
        return json.dumps({
            "keyword": "<keyword>",
            "type": "<type>",
            "value": "<value>",
            "default_value": "<default_value>",
            "description": "<description>",
            "regex": "<regex>",
            "required": "<required>",
            "widget": "<widget>",
            "enabled": "<enabled>",
            "visible": "<visible>",
            "order": "<order>",
            "options": { o:"<{}>".format(o) for o in cls.get_options() }
        })

    def serialize_json(self):
        """Return json representation of a keyword"""
        return json.dumps({
            "keyword": self.keyword,
            "type": self.type,
            "value": self.value,
            "default_value": self.default_value,
            "description": self.description,
            "regex": self.regex,
            "required": self.required,
            "widget": self.widget,
            "enabled": self.enabled,
            "visible": self.visible,
            "order": self.order,
            "options": json.loads(self.options) if self.options else json.dumps({})
        })


    def load_from_dict(self, d):
        """Store all parameters found in a dict
        This is used for importing data
        """
        required_fields = [ "keyword" ]
        
        # check if all required fields are there
        for x in required_fields:
            if (x not in d) and (not d[x]):
                ## TODO: throw error - field does not exist
                current_app.logger.warn("Required field {} is missing or emptry".format(x))
                return False

        stats = {
            "imported_keys": [],
            "failed_keys": [],
            "ignored_keys": [],
            "total": 0,
            "success": None
        }

        for x in d:
            current_app.logger.debug("import key, value: {}, {}".format(x, d[x]))
            stats["total"] += 1

            if x in [ "options" ]:
                if x == "options":
                    stats["ignored_keys"].append(x)
                # TODO:
                #  import options and facts
                continue

            current_value = None
            try:
                current_value = getattr(self, x)                
                current_type = type(self.__class__.__dict__[x])
                current_app.logger.debug("type of key = {}".format(current_type))
                sanitized = self.sanitize_key(d[x])
                if current_value:
                    current_app.logger.debug("key {} exists (type={}), old value = {}, new value = {}".format(x, current_type, current_value, sanitized))
                else:
                    current_app.logger.debug("key {} exists (type={}), new value = {}".format(x, current_type, sanitized))
                setattr(self, x, sanitized)
                stats["imported_keys"].append(x)
            except AttributeError as e:
                current_app.logger.exception(e)                
                current_app.logger.warn("key {} does not exist, ignore it".format(x))                
                stats["failed_keys"].append(x)
                pass
            except Exception as e:
                current_app.logger.exception(e)                
                stats["failed_keys"].append(x)
                pass

        if len(stats["failed_keys"]) > 0:
            stats["success"] = False
        else:
            stats["success"] = True

        return stats


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


    @classmethod
    def sample_json(cls):
        return json.dumps({
            "name": "<name>",
            "template": "<template>",
            "options": { o:"<{}>".format(o) for o in cls.get_options() }
        })


    def serialize_json(self):
        """Return json representation of a template"""
        return json.dumps({
            "name": self.name,
            "template": self.template,
            "options": json.loads(self.options) if self.options else json.dumps({})
        })


    def load_from_dict(self, d):
        """Store all parameters found in a dict
        This is used for importing data
        """
        required_fields = [ "name", "template" ]
        
        # check if all required fields are there
        for x in required_fields:
            if (x not in d) and (not d[x]):
                ## TODO: throw error - field does not exist
                current_app.logger.warn("Required field {} is missing or emptry".format(x))
                return False

        stats = {
            "imported_keys": [],
            "failed_keys": [],
            "ignored_keys": [],
            "total": 0,
            "success": None
        }

        for x in d:
            current_app.logger.debug("import key, value: {}, {}".format(x, d[x]))
            stats["total"] += 1

            if x in [ "options" ]:
                if x == "options":
                    stats["ignored_keys"].append(x)
                # TODO:
                #  import options and facts
                continue

            current_value = None
            try:
                current_value = getattr(self, x)                
                current_type = type(self.__class__.__dict__[x])
                current_app.logger.debug("type of key = {}".format(current_type))
                sanitized = self.sanitize_key(d[x])
                if current_value:
                    current_app.logger.debug("key {} exists (type={}), old value = {}, new value = {}".format(x, current_type, current_value, sanitized))
                else:
                    current_app.logger.debug("key {} exists (type={}), new value = {}".format(x, current_type, sanitized))
                setattr(self, x, sanitized)
                stats["imported_keys"].append(x)
            except AttributeError as e:
                current_app.logger.exception(e)                
                current_app.logger.warn("key {} does not exist, ignore it".format(x))                
                stats["failed_keys"].append(x)
                pass
            except Exception as e:
                current_app.logger.exception(e)                
                stats["failed_keys"].append(x)
                pass

        if len(stats["failed_keys"]) > 0:
            stats["success"] = False
        else:
            stats["success"] = True

        return stats


    def __repr__(self):
        return "<Template \'{}\'>".format(self.name)

