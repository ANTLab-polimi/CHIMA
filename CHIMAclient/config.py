from encapsulator.userspace import *

class GlobalConfig():
    def __init__(self):
        self.destinations = []
        self.interface = None
        self.encap = MPLS_encapsulator(100)
        self.installed_subnets = []
        self.installed_ips = []
        self.debug = False

conf = GlobalConfig()