import os
import time
import subprocess

from app import create_app
from flask_rq import get_queue
from flask import jsonify



def task_ping(hostname):
    output = subprocess.check_output(["ping", "-c", "5", hostname])
    return output.decode('ASCII')


def task_snmp(hostname, community, oid):
    output = subprocess.check_output(["snmpwalk", "-v", "2c", "-c", community, hostname, oid])
    return output.decode('ASCII')


def ping_device(hostname):
    response_object = {}
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
    response_object = {}
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
