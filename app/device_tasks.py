import os
import time
import subprocess

from app import create_app
from flask_rq import get_queue
from flask import jsonify

import uuid

def task_ping(hostname):
    output = subprocess.check_output(["ping", "-c", "5", hostname])
    return output.decode('ASCII')


def task_snmp(hostname, community, oid):
    output = subprocess.check_output(["snmpwalk", "-v", "2c", "-c", community, hostname, oid])
    return output.decode('ASCII')

def task_send_config_to_device(hostname, username, password, driver, config):
    # TODO: use python directly but for now save the commands to a temp file
    #       and pass the filename as argument
    cmdfile = "/tmp/{}".format(str(uuid.uuid4()))
    with open(cmdfile, 'w') as fd:
        fd.write(config)

    output = subprocess.check_output(["/bin/bash", "/Users/mwallraf/dev/flask-base/external_scripts/run-netmiko_test.sh",
                                        hostname,
                                        username,
                                        password,
                                        driver,
                                        cmdfile
                                    ],
                                    stderr=subprocess.STDOUT)
    return output.decode('ASCII')


def ping_device(hostname):
    task = get_queue().enqueue(task_ping, hostname)
    response_object = {
        'status': 'error',
        'data': {
            'task_id': ''
        }
    }        
    if task:
        response_object = {
            'status': 'success',
            'data': {
                'task_id': task.get_id()
            }
        }
    return jsonify(response_object), 202


def snmp_device(hostname, community="public", oid=".1.3.6.1.2.1.1"):
    """
    oid .1.3.6.1.2.1.1 = system
    """
    task = get_queue().enqueue(task_snmp, args=(hostname, community, oid))
    response_object = {
        'status': 'error',
        'data': {
            'task_id': ''
        }
    }        
    if task:
        response_object = {
            'status': 'success',
            'data': {
                'task_id': task.get_id()
            }
        }
    return jsonify(response_object), 202


def send_config_to_device(connection_details):
    response_object = {}
    hostname = connection_details["hostname"]
    username = connection_details["username"]
    password = connection_details["password"]
    transport = connection_details["transport"]
    driver = connection_details["driver"]
    config = connection_details["config"]

    if transport.lower() == "telnet":
        driver = driver + "_telnet"
    task = get_queue().enqueue(task_send_config_to_device, args=(hostname, username, password, driver, config))
    response_object = {
        'status': 'error',
        'data': {
            'task_id': ''
        }
    }        
    if task:
        response_object = {
            'status': 'success',
            'data': {
                'task_id': task.get_id()
            }
        }
    return jsonify(response_object), 202


def task_status(task_id):
    q = get_queue()
    task = q.fetch_job(task_id)
    if task:
        response_object = {
            'status': 'success',
            'data': {
                'task_id': task.get_id(),
                'task_status': task.get_status(),
                'task_result': str(task.result),
            }
        }
    else:
        response_object = {'status': 'error'}
    return jsonify(response_object)
