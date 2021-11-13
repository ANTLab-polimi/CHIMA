from ctypes import Array
from typing import Dict

from networkx.readwrite.json_graph import jit


class Device:
    def __init__(self, update):
        self.id = update["id"]
        self.INTcode = int(self.id[-2:])
        self.ports = {}

class Port:
    def __init__(self, update):
        self.number = update["number"]
        self.speed = update["speed"]
        self.name = update["name"]
        self.mac = update["mac"]
        self.link = None
        self.host = None

class Link:
    def __init__(self, update):
        self.dstDevice = update["dstDev"]
        self.dstPort = update["dstPort"]
        self.latency = None
        self.jitter = None

class Host:
    def __init__(self, update):
        self.mac = update["mac"]
        self.ip = update["ip"]
        self.docker = False
    
    def ips_list(self):
        output = ""
        for addr in self.ip:
            output += "%s; " % addr
        return output

class INTFunction:
    def __init__(self):
        self.latency = None
        self.jitter = None

def assignMetrics(latency, jitter, ids, network, int_funcs):
    #Reduces complexity under the assumption that a device
    #cannot be connected to itself
    for device in network:
        if ids[1] >= 100: #Function
            id = ids[1] - 100 #Get the correct id of the function
            if id in int_funcs:
                int_funcs[id].latency = latency
                int_funcs[id].jitter = jitter
        elif network[device].INTcode in ids:
            for port in network[device].ports.values():
                if port.link != None and int(port.link.dstDevice[-2:]) in ids:
                    port.link.latency = latency
                    port.link.jitter = jitter
                    #print(device.id + "->" + port.link.dstDevice + ": " + str(lat))
