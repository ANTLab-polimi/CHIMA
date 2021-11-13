import time

from utils import file_exists
from defines import *
from chimastub import *

## Installation of compiled pipelines on switches
def install_pipeline(deviceID, jsonPath, p4infoPath):
    if not file_exists(jsonPath): return
    if not file_exists(p4infoPath): return
    
    conf = {
                "deviceID" : deviceID,
                "json": jsonPath,
                "p4info": p4infoPath
            }

    chimastub = CHIMAstub(ONOS_ENDPOINT, ONOS_USER, ONOS_PSW)
    
    chimastub.install_pipeconf(conf)

    while not chimastub.check_pipeconf(conf):
        time.sleep(0.1)