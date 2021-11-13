import requests

CLIENT_PORT = 4243

class ClientRules:
    route = 0
    path = 1
    arp = 2
    ip = 3

class CHIMAclient:
    def __init__(self, ip):
        self.ip = ip
    
    def add_path(self, srcIP, dstIP, stack) -> bool:
        try:
            code = requests.post("http://%s:%s/path" % (self.ip, CLIENT_PORT), json={"src": srcIP, "dst": dstIP, "stack" : stack }, timeout=5).status_code
            if code == 200:
                return True
            else:
                raise Exception("Bad return code %d" % code)
        except Exception as ex:
            print("ERROR: request to the client %s failed (path)\n->%s" % (self.ip, ex) )
            return False
    
    def del_path(self, srcIP, dstIP) -> bool:
        try:
            code = requests.delete("http://%s:%s/path" % (self.ip, CLIENT_PORT), json={"src": srcIP, "dst": dstIP}, timeout=5).status_code
            if code == 200:
                return True
            else:
                raise Exception("Bad return code %d" % code)
        except Exception as ex:
            print("ERROR: request to the client %s failed (path)\n->%s" % (self.ip, ex) )
            return False
    
    ###################################################################################################################################### Deprecated
    # def add_route(self, subnet) -> bool:
    #     try:
    #         code = requests.post("http://%s:%s/route" % (self.ip, CLIENT_PORT), json={"subnet": subnet}, timeout=5).status_code
    #         if code == 200:
    #             return True
    #         else:
    #             raise Exception("Bad return code %d" % code)
    #     except Exception as ex:
    #         print("ERROR: request to the client %s failed (route)\n->%s" % (self.ip, ex) )
    #         return False

    # def del_route(self, subnet) -> bool:
    #     try:
    #         code = requests.delete("http://%s:%s/route" % (self.ip, CLIENT_PORT), json={"subnet": subnet}, timeout=5).status_code
    #         if code == 200:
    #             return True
    #         else:
    #             raise Exception("Bad return code %d" % code)
    #     except Exception as ex:
    #         print("ERROR: request to the client %s failed (route)\n->%s" % (self.ip, ex) )
    #         return False

    # def add_arp(self, ip, mac) -> bool:
    #     try:
    #         code = requests.post("http://%s:%s/arp" % (self.ip, CLIENT_PORT), json={"ip": ip, "mac" : mac }, timeout=5).status_code
    #         if code == 200:
    #             return True
    #         else:
    #             raise Exception("Bad return code %d" % code)
    #     except Exception as ex:
    #         print("ERROR: request to the client %s failed (arp)\n->%s" % (self.ip, ex) )
    #         return False
    
    # def del_arp(self, ip) -> bool:
    #     try:
    #         code = requests.delete("http://%s:%s/arp" % (self.ip, CLIENT_PORT), json={"ip": ip }, timeout=5).status_code
    #         if code == 200:
    #             return True
    #         else:
    #             raise Exception("Bad return code %d" % code)
    #     except Exception as ex:
    #         print("ERROR: request to the client %s failed (arp)\n->%s" % (self.ip, ex) )
    #         return False
    
    # def add_ip(self, ip) -> bool:
    #     try:
    #         code = requests.post("http://%s:%s/ip" % (self.ip, CLIENT_PORT), json={"ip": ip}, timeout=5).status_code
    #         if code == 200:
    #             return True
    #         else:
    #             raise Exception("Bad return code %d" % code)
    #     except Exception as ex:
    #         print("ERROR: request to the client %s failed (ip)\n->%s" % (self.ip, ex) )
    #         return False
    
    # def del_ip(self, ip) -> bool:
    #     try:
    #         code = requests.delete("http://%s:%s/ip" % (self.ip, CLIENT_PORT), json={"ip": ip }, timeout=5).status_code
    #         if code == 200:
    #             return True
    #         else:
    #             raise Exception("Bad return code %d" % code)
    #     except Exception as ex:
    #         print("ERROR: request to the client %s failed (ip)\n->%s" % (self.ip, ex) )
    #         return False