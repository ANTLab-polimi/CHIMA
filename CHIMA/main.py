#To run flask in its own thread
from chimastub import CHIMAstub
import threading
#To catch CTRL+C
import signal
import sys

from defines import *
from shell import *
from stub_rest import *
from chimastub import *
from local_network import localnet
from collector.userspace import *

#Removes the API port from the onos stub api
def cleanup(sig, frame):
    #Remove BPF program from the interface
    print("Removing BPF collector...")
    try:
        config.collector.remove_bpf_program()
    except Exception as e:
        print("ERROR: Unable to remove collector from the interface")

    #Uninstall active compose files
    print("Deactivating active deployments...")
    clean_deployments()

    chimastub = CHIMAstub(ONOS_ENDPOINT, ONOS_USER, ONOS_PSW)

    #Unregister from ONOS stub
    print("Unregistering from ONOS stub...")
    if not chimastub.unregister_program(FLASK_PORT):
        exit(1)
    
    #Delete installed INT intents
    for int in config.intents:
        if not chimastub.del_int_intent(int):
            exit(1)

    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    
    collector_polling = 0.1
    ewma = 4

    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == "--debug":
                debug = True
            elif sys.argv[i] == "--polling":
                if i+1 < len(sys.argv):
                    collector_polling = float(sys.argv[i+1])
                    print("Collector polling interval set to %f seconds" % collector_polling)
            elif sys.argv[i] == "--ewma":
                if i+1 < len(sys.argv):
                    ewma = int(sys.argv[i+1])
                    print("EWMA weight set to %u" % ewma)
    
    if not debug:
        logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

    #Run flask in another thread
    api = StubAPI(debug, FLASK_HOST, FLASK_PORT)
    flask = threading.Thread(target=run_stub_server)
    flask.daemon = True
    flask.start()
    
    chimastub = CHIMAstub(ONOS_ENDPOINT, ONOS_USER, ONOS_PSW)
    
    #Register the API port to onos
    print("Registering to the stub...")
    if not chimastub.register_program(FLASK_PORT):
        exit(1)

    #BPF collector object to allow removal from the interface
    #before closing the program
    config.collector = INT_collector(polling_interval=collector_polling, shr_ewma=ewma)
    config.interface = "veth_1"
    localnet.set_interface(config.interface)

    #Run collector in another thread
    print("Attaching BPF collector...")
    config.collector.attach_bpf_program(config.interface)
    bpf = threading.Thread(target=config.collector.send_metrics, args=[network, int_funcs])
    bpf.daemon = True
    bpf.start()

    #Start INT with CHIMA stub
    print("Installing INT intents...")

    UDPconf = { "srcIP": localnet.subnet, "dstIP": localnet.subnet, "proto":"UDP" }
    response = chimastub.add_int_intent(UDPconf)

    if response == None:
        exit(1)
    
    config.intents = config.intents + response

    #Hang
    CHIMAshell().cmdloop()
    cleanup(None, None)