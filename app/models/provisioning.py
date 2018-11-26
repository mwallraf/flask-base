from .. import db
import json

class ProvisioningTemplate(db.Model):
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
    options = db.Column(db.Text, default=json.dumps({
                    "description": "", 
                    "hardware": "", 
                    "software": "", 
                    "created_by": "",
                    "created": ""
    }))
    enabled = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return "<Template \'{}\'>".format(self.name)

