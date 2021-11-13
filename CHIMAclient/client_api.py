#!/usr/bin/python3
from flask import Flask
from flask import request
from flask import send_file
app = Flask(__name__)

#To suppress Flask's request logs on stdout
import logging

from config import *
from mpls import *
from utils import *
from encapsulator.userspace import *

#Configured with StubAPI's constructor
CLIENT_FLASK_HOST = ""
CLIENT_FLASK_PORT = ""

class ClientAPI:
    #Flask method's can't be defined in a class
    #Configuration parameters are set as global variables through this class
    def __init__(self, host, port):
        global DEBUG, CLIENT_FLASK_HOST, CLIENT_FLASK_PORT
        CLIENT_FLASK_HOST = host
        CLIENT_FLASK_PORT = port

#Runs the flask server in a thread
def run_client_server():
    global app
    if not conf.debug:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    app.run(host=CLIENT_FLASK_HOST, port=CLIENT_FLASK_PORT)

#Get new destination / stack association
@app.route('/path', methods=['POST'])
def add_destination():
    data = request.json

    new = mpls_stack()
    for val in data["stack"]:
        new.add_label(val)

    print("New path %s -> %s, stack: %s, size: %d" % (data["src"], data["dst"], new, new.size) )
    
    src = ip2int(data["src"])
    dst = ip2int(data["dst"])
    
    conf.destinations.append((src,dst))
    conf.encap.map_inject(src, dst, new)
    return "OK"

#Delete destination
@app.route('/path', methods=['DELETE'])
def del_destination():
    data = request.json

    print("Deleting path %s -> %s" % (data["src"], data["dst"]) )

    src = ip2int(data["src"])
    dst = ip2int(data["dst"])

    if (src,dst) in conf.destinations:
        conf.destinations.remove((src, dst))
        conf.encap.map_remove(src, dst)
    return "OK"

#Get new ip route
@app.route('/route', methods=['POST'])
def new_route():
    data = request.json

    set_route(conf.interface, data["subnet"])
    conf.installed_subnets.append(data["subnet"])
    return "OK"

#Remove ip route
@app.route('/route', methods=['DELETE'])
def del_route():
    data = request.json

    remove_route(data["subnet"])
    if data["subnet"] in conf.installed_subnets:
        conf.installed_subnets.remove(data["subnet"])
    return "OK"

#Get new static arp
@app.route('/arp', methods=['POST'])
def new_arp():
    data = request.json

    set_arp(conf.interface, data["ip"], data["mac"])
    conf.installed_ips.append(data["ip"])
    return "OK"

#Remove static arp
@app.route('/arp', methods=['DELETE'])
def del_arp():
    data = request.json

    remove_arp(conf.interface, data["ip"])
    if data["ip"] in conf.installed_ips:
        conf.installed_ips.remove(data["ip"])
    return "OK"

#Get new ip
@app.route('/ip', methods=['POST'])
def new_ip():
    data = request.json

    set_ip(conf.interface, data["ip"])
    return "OK"

#Remove static arp
@app.route('/ip', methods=['DELETE'])
def del_ip():
    data = request.json

    remove_ip(conf.interface, data["ip"])
    return "OK"