ONOS_USER = 'onos'
ONOS_PSW = 'rocks'
ONOS_ENDPOINT = "http://localhost:8181/onos/"
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 4242

BASE_TEMPLATE_PATH = "./templating/base_template.p4"
BASE_BUILD_SCRIPT = "./templating/bmv2-compile.sh"

TMP_PATH = "/tmp/CHIMA/"

#Collections of current components
network = {}

#Collection of function telemetries
int_funcs = {}

debug = False

#To record installed INT intents
class GlobalConfig():
    def __init__(self) -> None:
        self.collector = None
        self.interface = None
        self.intents = []

config = GlobalConfig()