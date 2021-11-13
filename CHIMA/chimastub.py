import requests

class CHIMAstub:
    def __init__(self, endpoint, user, psw):
        self.endpoint = endpoint
        self.user = user
        self.password = psw

    def add_int_intent(self, intent):
        try:
            response = requests.post("%schima/int/" % (self.endpoint), auth=(self.user, self.password), json=intent)
            if response.status_code == 200:
                return response.json()["intentID"]
            else:
                raise Exception("Bad return code %d" % response.status_code)
        except Exception as ex:
            print("ERROR: Unable to start INT monitoring. Is the FM Stub activated in ONOS?\n->%s" % ex )
            return None
    
    def del_int_intent(self, code) -> bool:
        try:
            code = requests.delete("%schima/int/%s" % (self.endpoint, code), auth=(self.user, self.password)).status_code
            if code == 200:
                return True
            else:
                raise Exception("Bad return code %d" % code)
        except Exception as ex:
            print("ERROR: Unable to remove intents for INT monitoring.\n->%s" % ex )
            return False

    def register_program(self, port) -> bool:
        try:
            code = requests.post("%schima/register/%u" % (self.endpoint, port), auth=(self.user, self.password)).status_code
            if code == 200:
                return True
            else:
                raise Exception("Bad return code %d" % code)
        except Exception as ex:
            print("ERROR: Unable to register port to ONOS stub.\n->%s" % ex )
            return False
    
    def unregister_program(self, port) -> bool:
        try:
            code = requests.delete("%schima/register/%u" % (self.endpoint, port), auth=(self.user, self.password)).status_code
            if code == 200:
                return True
            else:
                raise Exception("Bad return code %d" % code)
        except Exception as ex:
            print("ERROR: Unable to remove port from ONOS stub.\n->%s" % ex )
            return False
    
    def install_pipeconf(self, conf) -> bool:
        try:
            code = requests.post("%schima/pipeconf" % (self.endpoint), auth=(self.user, self.password), json=conf).status_code
            if code == 200:
                return True
            else:
                raise Exception("Bad return code %d" % code)
        except Exception as ex:
            print("ERROR: Bad response while installing pipeconf on %s\n->%s" % (conf["deviceID"], ex))
            return False
    
    def check_pipeconf(self, conf) -> bool:
        try:
            response = requests.post("%schima/pipeconf/check" % (self.endpoint), auth=(self.user, self.password), json=conf)
            if response.status_code == 200:
                return response.json()["ready"] == 1
            else:
                raise Exception("Bad return code %d" % response.status_code)
        except Exception as ex:
            print("ERROR: Bad response while checking pipeconf on %s\n->%s" % (conf["deviceID"], ex))
            return False
