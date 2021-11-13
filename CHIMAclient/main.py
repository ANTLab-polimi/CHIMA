#To run flask in its own thread
import threading
import sys
import os
import logging
import time
#To catch CTRL+C
import signal

import requests
import traceback

from config import *
from client_api import *
from encapsulator.userspace import *

CLIENT_HOST = "0.0.0.0"
CLIENT_PORT = 4243

#Gracefully handle CTRL+C
def cleanup(sig, frame):
    print("Removing BPF program...")
    try:
        conf.encap.remove_bpf_program()
    except:
        print("ERROR: Couldn't remove BPF filter from the interface.")
    print("BPF program removed")
    print("Removing installed rules...")
    clean_installed_rules(conf.installed_subnets, conf.interface, conf.installed_ips)
    print("Removed all rules")
    os._exit(0) #For some reason the usual exit function didn't close the flask thread

if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)

    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == "--debug":
                conf.debug = True
            elif sys.argv[i] == "-i":
                if i+1 < len(sys.argv):
                    conf.interface = sys.argv[i+1]
    
    if not conf.debug:
        logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

    #Run encapsulator in another thread
    try:
        conf.encap.attach_bpf_program(conf.interface)
    except:
        print("ERROR: Unable to install bpf program to interface %s. Does the interface exist?" % conf.interface)
        exit(1)
    bpf = threading.Thread(target=conf.encap.manage_runtime)
    bpf.daemon = True
    bpf.start()

    #Run flask in another thread
    api = ClientAPI(CLIENT_HOST, CLIENT_PORT)
    flask = threading.Thread(target=run_client_server)
    flask.daemon = True
    flask.start()

    #Hang
    print(""" _____  _   _ ________  ___  ___       _ _            _   
/  __ \| | | |_   _|  \/  | / _ \     | (_)          | |  
| /  \/| |_| | | | | .  . |/ /_\ \ ___| |_  ___ _ __ | |_ 
| |    |  _  | | | | |\/| ||  _  |/ __| | |/ _ \ '_ \| __|
| \__/\| | | |_| |_| |  | || | | | (__| | |  __/ | | | |_ 
 \____/\_| |_/\___/\_|  |_/\_| |_/\___|_|_|\___|_| |_|\__|
""")

    while True:
        time.sleep(60)