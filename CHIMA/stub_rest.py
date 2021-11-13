#!/usr/bin/python3
from flask import Flask
from flask import request
from flask import send_file
app = Flask(__name__)

#To work with ONOS APIs
import requests
#To suppress Flask's request logs on stdout
import logging

from defines import *

#Import utils
from utils import *

#Components definitions
from components import *

#Configured with StubAPI's constructor
STUB_FLASK_HOST = ""
STUB_FLASK_PORT = ""
DEBUG = False

class StubAPI:
    #Flask method's can't be defined in a class
    #Configuration parameters are set as global variables through this class
    def __init__(self, debug, host, port):
        global DEBUG, network, STUB_FLASK_HOST, STUB_FLASK_PORT
        DEBUG = debug
        STUB_FLASK_HOST = host
        STUB_FLASK_PORT = port

#Runs the flask server in a thread
def run_stub_server():
    global app
    if not DEBUG:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    app.run(host=STUB_FLASK_HOST, port=STUB_FLASK_PORT)

#Show a textual representation of the topology
#in a web page
@app.route('/topo', methods=['GET'])
def show_topology():
    return dump_topology(network, "<br>", "├─")

#Show a visual representation of the topology
#in a web page
@app.route('/graph', methods=['GET'])
def show_graph():
    graph_topology(network)
    return send_file(GRAPH_FILE_NAME)

#Update the local representation of devices
@app.route('/update/device', methods=['POST'])
def update_device():
    data = request.json

    if DEBUG:
        print("Device %s %s" %(data["id"], data["available"]))

    if data["available"] == "YES":
        if data["id"] not in network:
            network[data["id"]] = Device(data)
    elif data["available"] == "NO" and data["id"] in network:
        del network[data["id"]]
    else:
        print("ERROR: update device " + data["id"])
    return "OK"

#Update the local representation of ports
@app.route('/update/port', methods=['POST'])
def update_port():
    data = request.json

    if DEBUG:
        print("Device %s Port %u %s" %(data["id"], data["number"], data["enabled"]))

    if data["id"] not in network:
        network[data["id"]] = Device(data)
    
    device = network[data["id"]]

    if data["enabled"] == "YES":
        device.ports[str(data["number"])] = Port(data)
    elif data["enabled"] == "NO" and str(data["number"]) in device.ports:
        del device.ports[str(data["number"])]
    elif data["enabled"] != "YES":
        print("ERROR: update port " + data["id"] + "/" + str(data["number"]))
        
    return "OK"

#Update the local representation of links
@app.route('/update/link', methods=['POST'])
def update_link():
    data = request.json
    src = data["srcDev"] + "/" + str(data["srcPort"])
    dst = data["dstDev"] + "/" + str(data["dstPort"])

    if DEBUG:
        print("Link %s<->%s %s" %(src, dst, data["state"]))

    if data["srcDev"] in network and str(data["srcPort"]) in network[data["srcDev"]].ports:
        port = network[data["srcDev"]].ports[str(data["srcPort"])]
        if data["state"] == "ACTIVE":
            port.link = Link(data)

            #Link and host should not be on the same port
            if(port.link != None and port.host != None):
                print("WARNING: both host and link registered on %s/%u" %(data["srcDev"], data["srcPort"]) )
        elif data["state"] == "INACTIVE" and port.link != None:
            port.link = None
        else:
            print("ERROR: update link")
    elif data["state"] != "INACTIVE":
        print("ERROR: update link, port not found: " + src + " <-> " + dst)
    return "OK"

#Update the local representation of hosts
@app.route('/update/host', methods=['POST'])
def update_host():
    data = request.json

    if DEBUG:
        print("Host %s<->%s/%u %s" %(data["ip"][0], data["device"], data["port"], data["available"]))

    if data["device"] in network and str(data["port"]) in network[data["device"]].ports:
        port = network[data["device"]].ports[str(data["port"])]
        if data["available"] == "YES":
            new_host = Host(data)
            port.host = new_host

            #Link and host should not be on the same port
            if(port.link != None and port.host != None):
                print("WARNING: both host and link registered on %s/%u" %(data["device"], data["port"]) )
            
            #Check if the host has a Docker Engine
            try:
                #If the request has no response, the machine does not expose a Docker Engine
                requests.get("http://%s:2375/version" %(data["ip"]), timeout=2)
                port.host.docker = True
            except:
                port.host.docker = False
        elif data["available"] == "YES" and port.host != None:
            port.host = None
        else:
            print("ERROR: update host")
    elif data["available"] != "NO":
        print("ERROR: update host, port not found: %s<->%s/%u" %(data["ip"], data["device"], data["port"]))
    return "OK"