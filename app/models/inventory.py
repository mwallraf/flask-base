from .. import db
import json
from datetime import datetime
from flask_login import current_user
from app.models.user import User
from app.models.miscellaneous import BaseModelWithOptions
from sqlalchemy import desc, Table
from config import Config
from flask import current_app



class InventoryCustomer(BaseModelWithOptions):
    """
    Class to define a customer - prepare for multi-homed setup
    """
    __tablename__ = 'inventory_customer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    enabled = db.Column(db.Boolean, default=True)

    sites = db.relationship("InventorySite")

    options = db.Column(db.Text, default=json.dumps({
    }))

    @classmethod
    def get_options(cls):
        """
        Returns the individual options that can be used in the options field
        In order that should be displayed in HTML
        """
        return []

    @staticmethod
    def insert_default_customer(customer_name=Config.APP_DEFAULT_CUSTOMER):
        """Initiate the application with a default customer"""

        default_customer = InventoryCustomer.query.filter_by(name=customer_name).first()
        if default_customer is None:
            default_customer = InventoryCustomer(name=customer_name)
            db.session.add(default_customer)
            db.session.commit()

    @staticmethod
    def default_customer_id():
        customer = InventoryCustomer.query.filter_by(name=Config.APP_DEFAULT_CUSTOMER).first()
        return customer.id

    @staticmethod
    def default_customer():
        customer = InventoryCustomer.query.filter_by(name=Config.APP_DEFAULT_CUSTOMER).first()
        return customer


    def __repr__(self):
        return "<Customer \'{}\'>".format(self.name)




class InventorySite(BaseModelWithOptions):
    """
    Store sites that an inventory device can belong to
    Each site should be connected to a Customer
    """
    __tablename__ = 'inventory_site'

    id = db.Column(db.Integer, primary_key=True)
    siteid = db.Column(db.String(100), unique=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)
    region = db.Column(db.String)
    enabled = db.Column(db.Boolean, default=True)
    visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=lambda: current_user.get_id())
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=lambda: current_user.get_id(), onupdate=lambda: current_user.get_id())
    customer_id = db.Column(db.Integer, db.ForeignKey('inventory_customer.id'), default=lambda: InventoryCustomer().default_customer_id())

    created_by = db.relationship("User", foreign_keys=[created_by_id])
    updated_by = db.relationship("User", foreign_keys=[updated_by_id])
    customer = db.relationship("InventoryCustomer", foreign_keys=[customer_id], back_populates="sites")

    devices = db.relationship("InventoryDevice")

    options = db.Column(db.Text, default=json.dumps({
        "criticality": "",
        "wan_owner": ""
    }))

    # only serialize the keys defined here
    # required keys will always be returned, even when null or empty
    # (key, required)
    serialize_keys = [
            ("id", True),
            ("siteid", True),
            ("name", True),
            ("address", False),
            ("city", True),
            ("country", True),
            ("region", True),
            ("enabled", True),
            ("visible", True),
            ("customer", True),
            ("options", True),
    ]

    @classmethod
    def get_options(cls):
        """
        Returns the individual options that can be used in the options field
        In order that should be displayed in HTML
        """
        return ["criticality", "wan_owner"]


    @staticmethod
    def insert_default_site(site_id="Default site"):
        """Initiate the application with a default customer"""

        default_site = InventorySite.query.filter_by(siteid=site_id).first()
        if default_site is None:
            default_site = InventorySite(
                                            siteid=site_id,
                                            name=site_id
            )
            db.session.add(default_site)
            db.session.commit()

    @staticmethod
    def default_site_id():
        site = InventorySite.query.filter_by(siteid="Default site").first()
        return site.id

    @staticmethod
    def default_site():
        site = InventorySite.query.filter_by(siteid="Default site").first()
        return site


    @classmethod
    def sample_json(cls):
        return json.dumps({
            "siteid": "<siteid>",
            "name": "<name>",
            "address": "<address>",
            "city": "<city>",
            "country": "<country>",
            "region": "<region>",
            "enabled": "<enabled>",
            "visible": "<visible>",
            "customer": "<customer>",
            "options": { o:"<{}>".format(o) for o in cls.get_options() },
        })


    def __serialize_json(self):
        """Return json representation of a site"""
        return json.dumps({
            "siteid": self.siteid,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "country": self.country,
            "region": self.region,
            "enabled": self.enabled,
            "visible": self.visible,
            "customer": self.customer.name if self.customer else None,
            "options": json.loads(self.options) if self.options else json.dumps({})
            })



    def load_from_dict(self, d):
        """Store all parameters found in a dict
        This is used for importing data
        """
        required_fields = [ "siteid" ]
        
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

            if x in [ "customer", "options" ]:
                if x == "customer":
                    self.customer = InventoryCustomer.query.filter_by(name=d[x]).first()
                    if not self.customer:
                        self.customer = InventoryCustomer().default_customer()
                    stats["imported_keys"].append(x)
                else:
                    stats["ignored_keys"].append(x)
                # TODO:
                #  import options
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
        return "<Site \'{}\'>".format(self.siteid)


# many-to-many relation between InventoryPool and InventoryDevice
inventory_pool_device_table = Table(
    'inventory_pool_device_association',
    db.Model.metadata,
    db.Column('pool_id', db.Integer, db.ForeignKey('inventory_pool.id')),
    db.Column('device_id', db.Integer, db.ForeignKey('inventory_device.id'))
)



class InventoryPool(BaseModelWithOptions):
    """
    Class to define a pool of devices.
    This has a many-many relationship with InventoryDevice
    """
    __tablename__ = 'inventory_pool'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String())
    enabled = db.Column(db.Boolean, default=True)
    visible = db.Column(db.Boolean, default=True)
    dynamic = db.Column(db.Boolean, default=False)  # requires a device filter
    dynamic_filter = db.Column(db.String())         # device filter for dynamic resources

    devices = db.relationship('InventoryDevice', 
        secondary=inventory_pool_device_table,
        back_populates='pools'
    )

    options = db.Column(db.Text, default=json.dumps({
    }))

    @classmethod
    def get_options(cls):
        """
        Returns the individual options that can be used in the options field
        In order that should be displayed in HTML
        """
        return ["username", "password", "enable_password", "driver"]

    @staticmethod
    def insert_default_pool(pool_name="All devices"):
        """Initiate the application with a default customer"""

        default_pool = InventoryPool.query.filter_by(name=pool_name).first()
        if default_pool is None:
            default_pool = InventoryPool(name=pool_name)
            db.session.add(default_pool)
            db.session.commit()

    @staticmethod
    def default_pool_id():
        pool = InventoryPool.query.filter_by(name="All devices").first()
        return pool.id


    def __repr__(self):
        return "<Pool \'{}\'>".format(self.name)



class InventoryDevice(BaseModelWithOptions):
    """
    Store sites that an inventory device can belong to
    Each site should be connected to a Customer
    This has a many-many relationship with InventoryPool
    """
    __tablename__ = 'inventory_device'

    id = db.Column(db.Integer, primary_key=True)
    deviceid = db.Column(db.String(100), unique=True) # unique identifier
    managementip = db.Column(db.String, unique=False) # multi-VRF ex
    hostname = db.Column(db.String, unique=False)     # multi-VRF ex
    domain = db.Column(db.String)    
    enabled = db.Column(db.Boolean, default=True)
    visible = db.Column(db.Boolean, default=True)
    active = db.Column(db.Boolean, default=True)
    alias = db.Column(db.String) # comma seperated list of aliases
    source = db.Column(db.String) # ex: manual input, discovered, solarwinds, ...
    hwmodel = db.Column(db.String)
    swversion = db.Column(db.String)
    vendor = db.Column(db.String)
    networks = db.Column(db.String) # comma seperated list of networks
    driver = db.Column(db.String)  # ex napalm driver: cisco_ios, cisco_wlc, hp_procurve, ..
    function = db.Column(db.String) # see INVENTORY_DEVICE_FUNCTIONS in config file
    username = db.Column(db.String) # override global or pool settings
    password = db.Column(db.String) # override global or pool settings
    enable_password = db.Column(db.String) # override global or pool settings
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    firstseen_at = db.Column(db.DateTime())
    lastseen_at = db.Column(db.DateTime())
    status = db.Column(db.String) # ex ACTIVE, UNKNOWN, DISCOVERED, PROVISIONED, DECOMMISSIONED, ...

    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=lambda: current_user.get_id())
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=lambda: current_user.get_id(), onupdate=lambda: current_user.get_id())
    site_id = db.Column(db.Integer, db.ForeignKey('inventory_site.id'), default=lambda: InventorySite().default_site_id())

    created_by = db.relationship("User", foreign_keys=[created_by_id])
    updated_by = db.relationship("User", foreign_keys=[updated_by_id])
    site = db.relationship("InventorySite", foreign_keys=[site_id], back_populates="devices")

    pools = db.relationship('InventoryPool', 
        secondary=inventory_pool_device_table,
        back_populates='devices'
    )

    # options are a dict of key_value pairs with extra options or fields
    # not defined directly in the database
    options = db.Column(db.Text, default=json.dumps({
    }))

    # facts are like options but each key is another dict
    # this allows extra fields per fact
    # A fact can be a application specific plugin for example
    facts = db.Column(db.Text, default=json.dumps({
    }))

    # only serialize the keys defined here
    # required keys will always be returned, even when null or empty
    # (key, required)
    serialize_keys = [
            ("id", True),
            ("deviceid", True),
            ("managementip", True),
            ("hostname", True),
            ("domain", True),
            ("enabled", True),
            ("visible", True),
            ("active", True),
            ("alias", True),
            ("source", False),
            ("hwmodel", False),
            ("swversion", False),
            ("vendor", False),
            ("networks", False),
            ("driver", False),
            ("function", True),
            ("username", False),
            ("password", False),
            ("enable_password", False),
            ("status", True),
            ("site", True),
            ("options", True),
            ("facts", True),
    ]


    @classmethod
    def sample_json(cls):
        return json.dumps({
            "deviceid": "<deviceid>",
            "managementip": "<managementip>",
            "hostname": "<hostname>",
            "domain": "<domain>",
            "enabled": "<enabled>",
            "visible": "<visible>",
            "active": "<active>",
            "alias": "<alias>",
            "source": "<source>",
            "hwmodel": "<hwmodel>",
            "swversion": "<swversion>",
            "vendor": "<vendor>",
            "networks": "<networks>",
            "driver": "<driver>",
            "function": "<function>",
            "username": "<username>",
            "password": "<password>",
            "enable_password": "<enable_password>",
            "status": "<status>",
            "site": "<site>",
            "options": { o:"<{}>".format(o) for o in cls.get_options() },
            "facts": { f:"<{}>".format(f) for f in cls.get_facts() }
        })



    def load_from_dict(self, d):
        """Store all parameters found in a dict
        This is used for importing data
        """
        required_fields = [ "deviceid", "managementip", "hostname" ]
        
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

            # for none-standard sring values we need a seperate action
            if x in [ "site", "siteid", "options", "facts" ]:
                if x in [ "site", "siteid" ]:
                    self.site = InventorySite.query.filter_by(siteid=d[x]).first()
                    if not self.site:
                        self.site = InventorySite().default_site()
                    stats["imported_keys"].append(x)
                elif x in [ "facts", "options" ]:
                    dict_a = json.loads(getattr(self, x))
                    dict_a.update(d[x])
                    setattr(self, x, str(json.dumps(dict_a)))
                else:
                    stats["ignored_keys"].append(x)
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

    @classmethod
    def get_options(cls):
        """
        Returns the individual options that can be used in the options field
        In order that should be displayed in HTML
        """
        return []

    @classmethod
    def get_facts(cls):
        """
        Returns the individual options that can be used in the options field
        In order that should be displayed in HTML
        """
        return [ x[0] for x in Config.INVENTORY_ENABLED_FACTS ]


    def __repr__(self):
        return "<Device \'{}\'>".format(self.name)

