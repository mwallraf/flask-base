from flask import current_app
import json
from app.models.inventory import InventoryDevice, InventorySite
from app.models.provisioning import ProvisioningKeyword, ProvisioningTemplate
from app import db


SUPPORTED_IMPORT_EXPORT_OBJECTS = [ "sites", "devices", "keywords", "templates" ]


def export_json_file():
    """
    Returns a JSON text file
    """
    sites = [ json.loads(site.serialize_json()) for site in InventorySite.query.all() ]
    devices = [ json.loads(device.serialize_json()) for device in InventoryDevice.query.all() ]
    templates = [ json.loads(template.serialize_json()) for template in ProvisioningTemplate.query.all() ]
    keywords = [ json.loads(keyword.serialize_json()) for keyword in ProvisioningKeyword.query.all() ]

    content =  json.dumps({ "sites": sites, 
                            "devices": devices,
                            "templates": templates,
                            "keywords": keywords
                            }, 
                            indent=4)
    return content


def export_json_file_sample():
    """
    Returns a JSON text file with sample data
    """
    content = json.dumps({"sites": [ json.loads(InventorySite.sample_json()) ],
                          "devices": [ json.loads(InventoryDevice.sample_json()) ],
                          "templates": [ json.loads(ProvisioningTemplate.sample_json()) ],
                          "keywords": [ json.loads(ProvisioningKeyword.sample_json()) ],
                          },
                          indent=4)
    return content


def import_json_file(f):
    """
    Read a json import file f and import the contents into the DB
    Currently supported:
      - sites
      - devices
    """
    current_app.logger.debug("Reading file: {}".format(f.filename))

    total_stats = {}
    for stat in SUPPORTED_IMPORT_EXPORT_OBJECTS:
        total_stats[stat] = {
            "imported": [],
            "failed": [],
            "success": None
        }

    try:
        f.seek(0)
        j = json.loads(f.read())
        current_app.logger.debug("Import file contents = {}".format(json.dumps(j, indent=4)))

        # import supported objects only
        for o in SUPPORTED_IMPORT_EXPORT_OBJECTS:
            if o in j:
                current_app.logger.debug("Importing {}:".format(o))

                for item in j[o]:

                    obj = None
                    # check if a the object exists
                    if o == "devices" and "deviceid" in item:
                        obj = InventoryDevice.query.filter_by(deviceid=item["deviceid"]).first()
                        if obj is None:
                            obj = InventoryDevice()
                    elif o == "sites" and "siteid" in item:
                        obj = InventorySite.query.filter_by(siteid=item["siteid"]).first()
                        if obj is None:
                            obj = InventorySite()
                    elif o == "keywords" and "keyword" in item:
                        obj = ProvisioningKeyword.query.filter_by(keyword=item["keyword"]).first()
                        if obj is None:
                            obj = ProvisioningKeyword()
                    elif o == "templates" and "name" in item:
                        obj = ProvisioningTemplate.query.filter_by(name=item["name"]).first()
                        if obj is None:
                            obj = ProvisioningTemplate()
                    if not obj:
                        # unsupported object type
                        continue

                    # import the dictionary into the object
                    rc = obj.load_from_dict(item)
                    if rc["success"]:
                        total_stats[o]["imported"].append(rc)
                    else:
                        total_stats[o]["failed"].append(rc)

                    current_app.logger.debug("New object imported: {}".format(obj.serialize_json()))

                    db.session.add(obj)
                    db.session.commit()

    except Exception as e:
        current_app.logger.exception(e)
        current_app.logger.error("Unable to open and parse import file: {}".format(f))
        pass

    for stat in total_stats:
        if len(total_stats[stat]["failed"]) > 0:
            total_stats[stat]["success"] = False
        else:
            total_stats[stat]["success"] = True

    return total_stats


