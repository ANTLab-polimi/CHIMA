import yaml
import os
from multiprocessing import Process
from threading import Thread
from shutil import copy
from collections import OrderedDict

from utils import *
from containers import *
from pipelines import *
from templating.templates import *
from mpls import *
from chimaclient import *
from triggers import *
from chimastub import *
from local_network import localnet
from components import *

FUNCTIONS_DIR = "functions"
COMPOSE_DIR = "compose"
OUTPUTS_DIR = "build"

class Deployment:
    def __init__(self, name, service):
        self.composes =  []
        self.rules = []
        self.switches = []
        self.triggers = []
        self.int = []
        self.next = None
        self.depFile = name
        self.serviceFile = service

class Equivalence:
    def __eq__(self, o) -> bool:
        for attr in vars(self):
            if vars(o)[attr] != vars(self)[attr]:
                return False
        return True

class ComposeInstall (Equivalence):
    def __init__(self, filepath, device, id):
        self.file = filepath
        self.device = device
        self.id = id

class RuleInstall (Equivalence):
    def __init__(self, type:ClientRules, device, args):
        self.type = type
        self.device = device
        self.args = args

class SwitchInstall (Equivalence):
    def __init__(self, device, ids):
        self.device = device
        self.ids = ids

class TriggerInstall (Equivalence):
    def __init__(self, id):
        self.id = id

active_deployments = {}

##################################################################################################################### Main operations

# Reads a yaml file that contains the information needed
# to execute a deployment, and performs the necessary actions
def load_deployment(serviceFile, depFile):
    serviceFile = absolute_path(serviceFile)
    if not file_exists(serviceFile): return
    depFile = absolute_path(depFile)
    if not file_exists(depFile): return

    deployment = None
    with open(depFile, 'r') as stream: 
        try:
            deployment = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(f"{depFile} is not a valid yaml file")
            return

    service = None
    with open(serviceFile, 'r') as stream: 
        try:
            service = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(f"{serviceFile} is not a valid yaml file")
            return
    
    deployment = merge(deployment, service)
    
    if "functions" not in deployment:
        print("ERROR: no functions defition in the deployment")
        return

    active_deployments[depFile] = Deployment(depFile, serviceFile)
    if "next" in deployment:
        active_deployments[depFile].next = absolute_path(deployment["next"])
    dep_record = active_deployments[depFile]

    #Prepare the temporary folder
    create_directory(TMP_PATH)
    
    functions = deployment["functions"]
    functions = OrderedDict( sorted(functions.items(), key=lambda x: x[1]["id"]) )

    preload_hosts = []
    if "hosts" in deployment:
        preload_hosts = deployment["hosts"]

    preload_containers(functions, deployment["service"], preload_hosts)
    
    container_functions(functions, deployment["service"], dep_record)
    print("")

    preload_switches = []
    if "switches" in deployment:
        preload_switches = deployment["switches"]

    switch_functions(functions, preload_switches, dep_record)
    print("")

    install_path(deployment["path"], deployment["service"]["client"], deployment["service"]["ip"], deployment["service"]["client"], dep_record)
    
    print("")
    install_triggers(functions, deployment["service"], dep_record)
    print("")
    install_int(deployment["service"], dep_record)
    print("")
    print("The service is available at %s" % deployment["service"]["ip"])
    print("\n")

# Changes a current deployment to another one with the least downtime possible
def redeploy(previous, depFile):
    previous = absolute_path(previous)
    if not file_exists(previous): return
    if previous not in active_deployments:
        print("ERROR: Trying to redeploy an inexisting deployment")
        return

    depFile = absolute_path(depFile)
    if not file_exists(depFile): return

    deployment = None
    with open(depFile, 'r') as stream: 
        try:
            deployment = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print("This is not a valid yaml file")
            return

    prev_dep = active_deployments[previous]
    service = None
    with open(prev_dep.serviceFile, 'r') as stream: 
        try:
            service = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(f"{prev_dep.serviceFile} is not a valid yaml file")
            return

    deployment = merge(deployment, service)
    
    if "functions" not in deployment:
        print("ERROR: no functions defition in the deployment")
        return

    # Create a temporary deployment record and copy over things that stay the same
    new_dep = Deployment(depFile, prev_dep.serviceFile)
    new_dep.int = prev_dep.int
    
    functions = deployment["functions"]
    functions = OrderedDict( sorted(functions.items(), key=lambda x: x[1]["id"]) )
    
    take_timestamp("CONTAINERS")

    # Determine witch function have to be changed and which ones stay the same
    containerThr = Thread(target=change_container_functions, args=[functions, deployment["service"], prev_dep, new_dep])
    containerThr.start()

    take_timestamp("SWITCH")
    # Install new switch functions
    switchThr = Thread(target=change_switch_functions, args=[functions, prev_dep, new_dep])
    switchThr.start()

    containerThr.join()
    switchThr.join()
    
    take_timestamp("RULES")

    # Install new path on the client
    install_path(deployment["path"], deployment["service"]["client"], deployment["service"]["ip"], deployment["service"]["client"], new_dep)
    print("")

    undo_triggers(prev_dep)
    install_triggers(functions, deployment["service"], new_dep)

    take_timestamp("REDEPLOYED")
    print("The service is available at %s" % deployment["service"]["ip"])
    print("\n")

    # Remove obsolete containers, which should be the only ones remaining
    # in the previous deployment record
    undo_containers(prev_dep)
    print("\nchima>", end="")

    del active_deployments[previous]
    active_deployments[depFile] = new_dep

##################################################################################################################### Docker functions
def preload_containers(functions, service, hosts):
    compose_folder = os.path.join(TMP_PATH, COMPOSE_DIR)
    create_directory(compose_folder)

    containers = []
    for name in functions:
        if functions[name]["type"] == "container":
            new_path = process_compose_file(functions[name], service)
            containers.append(new_path)
    
    running_threads = []
    for h in hosts:
        print("Preloading compose files on host %s..." %(h))
        # Run container installations in parallel to save time on deployment
        thr = Thread(target=build_compose, args=[containers, h])
        thr.start()
        running_threads.append(thr)
    
    #Wait for all threads to join before starting switch installs
    for t in running_threads:
        t.join()

def build_compose(composes, host):
    for c in composes:
        composeBuild(c, host)

# Performs installation of the container functions
def container_functions(functions, service, dep_record):
    compose_folder = os.path.join(TMP_PATH, COMPOSE_DIR)
    create_directory(compose_folder)

    running_threads = []

    store = {}

    #Sorting functions based on the device on which the deployment has to be done    
    for name in functions:
        if functions[name]["type"] == "container":
            current = functions[name]

            if current["device"] not in store:
                store[current["device"]] = []
            store[current["device"]].append(current)

    for dev in store:
        names = ""
        for fun in store[dev]:
            names+=basename(fun["file"])+";"
        print("Installing compose files %s on device %s..." % (names, dev) )

        # Run container installations in parallel to save time on deployment
        thr = Thread(target=install_compose, args=[store[dev], dev, service])
        thr.start()
        running_threads.append(thr)

        for fun in store[dev]:
            int_funcs[fun["id"]] = INTFunction()
            dep_record.composes.append( ComposeInstall(get_compose_filepath(fun, compose_folder), fun["device"], fun["id"]) )
    
    for name in functions:
        if functions[name]["type"] == "container":
            current = functions[name]
            compose_paths(current, dep_record)

    #Wait for all threads to join before starting switch installs
    for t in running_threads:
        t.join()
    

# Determines what should be changed from a previous compose deployment
# and executes it
def change_container_functions(functions, service, prev_record, new_record):
    running_threads = []
    compose_folder = os.path.join(TMP_PATH, COMPOSE_DIR)
    for name in functions:
        if functions[name]["type"] == "container":
            current = functions[name]
            depFile = absolute_path(current["file"])
            if not file_exists(depFile): return
            new_compose_path = get_compose_filepath(current, compose_folder)
            new_compose_record = ComposeInstall(new_compose_path, current["device"], current["id"])
            
            #If it's the same, move it to the new deployment, otherwise install it
            if new_compose_record in prev_record.composes:
                prev_record.composes.remove(new_compose_record)
            else:
                print("Installing compose file %s on device %s..." % (basename(current["file"]), current["device"]) )
                # Run container installations in parallel to save time on deployment
                thr = Thread(target=install_compose, args=[[current], current["device"], service])
                thr.start()
                running_threads.append(thr)

                int_funcs[current["id"]] = INTFunction()
            
            new_record.composes.append(new_compose_record)
    
    take_timestamp("PATHS")

    for name in functions:
        if functions[name]["type"] == "container":
            current = functions[name]
            compose_paths(current, new_record)
    
    take_timestamp("W_CONTAINER")
    #Wait for all threads to join before starting switch installs
    for t in running_threads:
        t.join()
    
    take_timestamp("CONTAINER_OK")

def process_compose_file(compose, service):
    depFile = absolute_path(compose["file"])
    if not file_exists(depFile): return

    #Reading the provided compose file
    content = None
    with open(depFile, 'r') as stream: 
        try:
            content = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print("This is not a valid yaml file")
            return
    
    #Adding subnet information
    content["networks"] = {"chima": {"ipam": {"config": []}}}
    content["networks"]["chima"]["ipam"]["config"].append({"subnet": service["subnet"]})
    content["networks"]["chima"]["driver"] = "macvlan"
    content["networks"]["chima"]["driver_opts"] = {"parent": compose["iface"]}

    #Adding ip
    containers = content["services"]
    for name in containers:
        containers[name]["networks"] = {"chima": {"ipv4_address": compose["ip"]}}

    compose_folder = os.path.join(TMP_PATH, COMPOSE_DIR)

    #Dumping the resulting file
    new_compose_path = os.path.join(compose_folder, basename(depFile))
    with open(new_compose_path, 'w') as stream:
        yaml.dump(content, stream)
    
    return new_compose_path

def get_compose_filepath(compose, compose_folder):
    depFile = absolute_path(compose["file"])
    if not file_exists(depFile): return
    return os.path.join(compose_folder, basename(depFile))

# Manages the modification of the compose file and its execution
def install_compose(composes, device, service):
    to_install = []

    for compose in composes:
        new_compose_path = process_compose_file(compose, service)
        to_install.append(new_compose_path)

    if composeUp(to_install, device) != 0:
        print("ERROR: Can't install compose files")

def compose_paths(compose, dep_record):
    if "paths" in compose:
        for p in compose["paths"]:
            install_path(p["stack"], compose["ip"], p["dst"], compose["device"], dep_record)

##################################################################################################################### Switch functions

# Performs installation of the switch functions
def switch_functions(functions, preload_switches, dep_record):
    func_folder = os.path.join(TMP_PATH, FUNCTIONS_DIR)
    create_directory(func_folder)

    store = {}

    #Sorting functions based on the device on which the deployment has to be done
    for name in functions:
        if functions[name]["type"] == "switch":
            current = functions[name]
            if current["device"] not in store:
                store[current["device"]] = []
            store[current["device"]].append(current)

    running_threads = []

    for dev in store:
        print("Installing %d functions on device %s..." % (len(store[dev]), dev) )
        thr = Thread(target=install_p4, args=[store[dev], dev, dep_record])
        thr.start()
        running_threads.append(thr)
        if dev in preload_switches:
            preload_switches.remove(dev)

    for dev in preload_switches:
        print("Installing 0 functions on device %s..." % (dev) )
        thr = Thread(target=install_p4, args=[[], dev, dep_record])
        thr.start()
        running_threads.append(thr)

    for t in running_threads:
        t.join()

# Determines what should be changed from a previous switch deployment
# and executes it 
def change_switch_functions(functions, prev_record, new_record):
    store = {}

    #Sorting functions based on the device on which the deployment has to be done
    for name in functions:
        if functions[name]["type"] == "switch":
            current = functions[name]
            if current["device"] not in store:
                store[current["device"]] = []
            store[current["device"]].append(current)
    
    running_threads = []

    for dev in store:
        ids = []
        for f in store[dev]:
            ids.append(f["id"])

        install = SwitchInstall(dev, frozenset(ids))
        if install not in prev_record.switches:
            print("Installing %d functions on device %s..." % (len(store[dev]), dev) )
            thr = Thread(target=install_p4, args=[store[dev], dev, new_record])
            thr.start()
            running_threads.append(thr)
        else:
            new_record.switches.append(install)
            prev_record.switches.remove(install)

    take_timestamp("W_SWITCH")
    
    for t in running_threads:
        t.join()
    
    take_timestamp("SWITCH_OK")

# Manages the merged install of a group of functions to the same device
def install_p4(definitions, dev, dep_record):
    func_folder = os.path.join(TMP_PATH, FUNCTIONS_DIR)

    funcs = []
    ids = []
    for f in definitions:
        copy(absolute_path(f["file"]), func_folder)
        funcs.append(Function( os.path.join(FUNCTIONS_DIR, basename(f["file"])), f["control"], f["id"]))
        ids.append(f["id"])
        print("  Function %s on device %s" % (f["control"], dev) )
    
    p4_path = os.path.join(TMP_PATH, f"{dev}.p4")
    output_folder = os.path.join(TMP_PATH, OUTPUTS_DIR)
    make_template(funcs, p4_path)
    build_pipeline(p4_path, output_folder, dev)
    install_pipeline(dev, os.path.join(output_folder, f"{dev}.json"),  os.path.join(output_folder, f"{dev}_p4info.txt"))

    dep_record.switches.append( SwitchInstall(dev, frozenset(ids)) )

##################################################################################################################### Installation various rules

# Instantiates triggers from the values specified in the functions
def install_triggers(functions, service, dep_record):
    global triggers
    for name in functions:
        if "triggers" in functions[name]:
            fun = functions[name]
            tr = fun["triggers"]
            triggers[fun["id"]] = Trigger(dep_record)
            current = triggers[fun["id"]]
            for i in range(0, len(tr)):
                current.metrics.append(frozenset(tr[i]))
            if "latency" in fun:
                current.l_max = fun["latency"]
            if "jitter" in fun:
                current.j_max = fun["jitter"]
            if "variation" in fun:
                current.v_max = fun["variation"]

            dep_record.triggers.append(TriggerInstall(fun["id"]))
    
    #Global trigger
    if "triggers" in service:
        triggers[0] = Trigger(dep_record)
        current = triggers[0]
        current.endtoend = True
        tr = service["triggers"]
        for i in range(0, len(tr)):
            current.metrics.append(frozenset(tr[i]))
        if "latency" in service:
            current.l_max = service["latency"]
        if "jitter" in service:
            current.j_max = service["jitter"]
        if "variation" in service:
            current.v_max = service["variation"]
        
        dep_record.triggers.append(TriggerInstall(0))


# Install a path on a CHIMAclient
def install_path(path, src, dst, client, dep_record):
    chimaclient = CHIMAclient(client)
    stack = mpls_stack()

    for i in range(0, len(path)):
        type = 0
        if path[i]["type"]=="port":
            type = 2
        elif path[i]["type"]=="function":
            type = 1
        elif path[i]["type"]=="timestamp":
            type = 3
        else:
            print("ERROR: Unkown path type %s" % path[i]["type"])
            return

        label = mpls_encode_type( type, path[i]["value"], 0, 1 if i == len(path)-1 else 0, 64 )
        stack.add_label(label)
        path[i]["type"] == "port"

    print("Deploying path to %s: %s" % (client, stack) )
    if not chimaclient.add_path(src, dst, stack.stack):
        return

    dep_record.rules.append( RuleInstall(ClientRules.path, client, [src, dst]) )

# Install INT intent to monitor the current deployment
def install_int(service, dep_record):
    chimastub = CHIMAstub(ONOS_ENDPOINT, ONOS_USER, ONOS_PSW)

    for int in config.intents: #The global list only has the ones installed at the beginning
        if not chimastub.del_int_intent(int):
            return
    
    config.intents.clear()
    
    #Destination
    conf = { "srcIP": localnet.subnet, "dstIP": service["subnet"], "proto":"UDP", "dstPort": str(service["port"]) }
    response = chimastub.add_int_intent(conf)
    if response == None:
        return
    dep_record.int += response

    #Source
    conf = { "srcIP": service["subnet"], "dstIP": localnet.subnet, "proto":"UDP", "dstPort": str(service["port"]) }
    response = chimastub.add_int_intent(conf)
    if response == None:
        return
    dep_record.int += response


##################################################################################################################### Undoing deployments

def undo_containers(dep: Deployment):
    running_threads = []
    for c in dep.composes:
        print("Removing compose file %s on device %s..." % (basename(c.file), c.device) )
        thr = Thread(target=composeStop, args=[c.file, c.device])
        thr.start()
        running_threads.append(thr)
    for t in running_threads:
        t.join()

def undo_triggers(dep:Deployment):
    for t in dep.triggers:
        del triggers[t.id]
    dep.triggers.clear()

# Completely uninstall a deployment
def undo_deployment(dep : Deployment):
    undo_triggers(dep)

    for c in dep.composes:
        if c.id in int_funcs:
            del int_funcs[c.id]
    undo_containers(dep)
    
    #Undo client rules
    for r in dep.rules:
        if r.type == ClientRules.route:
            CHIMAclient(r.device).del_route(r.args[0])
        elif r.type == ClientRules.path:
            CHIMAclient(r.device).del_path(r.args[0], r.args[1])
        elif r.type == ClientRules.arp:
            CHIMAclient(r.device).del_arp(r.args[0])
        elif r.type == ClientRules.ip:
            CHIMAclient(r.device).del_ip(r.args[0])
    
    func_folder = os.path.join(TMP_PATH, FUNCTIONS_DIR)
    create_directory(func_folder)
    output_folder = os.path.join(TMP_PATH, OUTPUTS_DIR)
    
    #Undo INT intents
    chimastub = CHIMAstub(ONOS_ENDPOINT, ONOS_USER, ONOS_PSW)
    for int in dep.int: #The global list only has the ones installed at the beginning
        if not chimastub.del_int_intent(int):
            return
    
    #If this is the last deployment, start basic INT
    if len(active_deployments) == 1:
        UDPconf = { "srcIP": localnet.subnet, "dstIP": localnet.subnet, "proto":"UDP" }
        response = chimastub.add_int_intent(UDPconf)

        if response == None:
            return
        
        config.intents = config.intents + response

def undo_deployment_file(depFile):
    depFile = absolute_path(depFile)
    if not file_exists(depFile): return

    if depFile in active_deployments:
        undo_deployment(active_deployments[depFile])
        del active_deployments[depFile]
    else:
        print("The deployment is not active")

# Removes all the currently installed deployments 
def clean_deployments():
    for id in active_deployments:
        undo_deployment(active_deployments[id])