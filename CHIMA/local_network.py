#To determine initial INT ip subnet
import netifaces
import netaddr

class LocalNetwork():
    def __init__(self):
        self.iface = None
        self.subnet = None

    def set_interface(self, interface):
        self.iface = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]
        self.subnet = str(netaddr.IPNetwork('%s/%s' % (self.iface['addr'], self.iface['netmask'])))

localnet = LocalNetwork()