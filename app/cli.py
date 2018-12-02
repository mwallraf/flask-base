from tinydb import TinyDB, Query
import json
import ujson
from napalm.base.validate import compare
import re

tinydb_host_facts = "tinydb_hosts.json"
tinydb_site_facts = "tinydb_sites.json"

def inventory_all_devices():
    db = TinyDB(tinydb_host_facts)
    devices = [ d for d in db if "hostname" in d ]
    return devices


def inventory_device_details(hostname):
    db = TinyDB(tinydb_host_facts)
    q = Query()
    devices = db.search(q.hostname == hostname)

    if devices:
        return devices[0]

    return None


def inventory_device_add(device):
    db = TinyDB(tinydb_host_facts)
    q = Query()
    # set defaults
    if "ise" not in device:
        device["ise"] = { "present": False }
    db.upsert(device, q.hostname == device["hostname"])
    return True


def inventory_device_delete(hostname):
    db = TinyDB(tinydb_host_facts)
    q = Query()
    db.remove(q.hostname == hostname)
    return True    


def inventory_all_sites():
    db = TinyDB(tinydb_site_facts)
    return db


def inventory_site_add(site):
    db = TinyDB(tinydb_site_facts)
    q = Query()
    # set defaults
    if "ise" not in site:
        site["ise"] = { "present": False }
    db.upsert(site, q.siteid == site["siteid"])
    return True


def inventory_site_details(siteid):
    db = TinyDB(tinydb_site_facts)
    q = Query()
    sites = db.search(q.siteid == siteid)

    if sites:
        return sites[0]

    return None


def inventory_site_delete(siteid):
    db = TinyDB(tinydb_site_facts)
    q = Query()
    db.remove(q.siteid == siteid)
    return True    