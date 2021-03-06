from .. import db
import json
from datetime import datetime
from flask_login import current_user
from app.models.user import User
from app.models.miscellaneous import BaseModelWithOptions
from sqlalchemy import desc, Table
from config import Config
from flask import current_app


class UsefulLink(BaseModelWithOptions):
    """
    Class to store the useful links for the main dashboard
    """
    __tablename__ = 'useful_links'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(), unique=False)
    title = db.Column(db.String(), unique=False)
    short_descr = db.Column(db.String(), unique=False)
    long_descr = db.Column(db.String(), unique=False)
    tooltip = db.Column(db.String(), unique=False)
    img = db.Column(db.String(), unique=False) # filename of uploaded image
    enabled = db.Column(db.Boolean, default=True)


