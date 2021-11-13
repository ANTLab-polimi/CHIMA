from pyvis.network import Network
import collections.abc
import os
import time

GRAPH_FILE_NAME = os.path.abspath("network.html")

#Checks if a file exists and prints an error if
#it doesn't
def file_exists(path):
    if os.path.isfile(path):
        return True
    else:
        print(f"ERROR: file {path} does not exist.")
        return False

#Create file with correct permissions if
#it doesn't exist
def create_file(path):
    if not os.path.isfile(path):
        open(path, "w").close()
        os.chmod(path, 0o777)

def create_directory(path):
    if not os.path.isdir(path):
        os.mkdir(path, 0o777)

#Create file with correct permissions if
#it doesn't exist
def absolute_path(path):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    return path

#Returns only the name of the file from a complete path
def basename(path):
    return os.path.basename(path)

#Returns a string that represents the current network
#Alternative newline and tab representations can be specified
#for example to allow pretty printing in a web page
def dump_topology(network, int_funcs, newline="\n", tab="├─"):
    if len(network) == 0:
        return "*Nothing*"
    
    output = ""
    for id in network:
        output += id+":"+newline
        for p in network[id].ports:
            port = network[id].ports[p]
            output += tab + " " + str(port.number)
            if port.link != None:
                output += " -> %s/%u" % (port.link.dstDevice, port.link.dstPort)
                if port.link.latency != None and port.link.jitter != None:
                    output += "  [%u, %d]" % (port.link.latency, port.link.jitter)
            elif port.host != None:
                output += " -> %s" % (port.host.ips_list())
                if port.host.docker:
                    output += " [D]"
            output += newline

    for id in int_funcs:
        f = int_funcs[id]
        if f.latency != None and f.jitter != None:
            output += newline
            output += "Function %s: [%u, %u]" % (id, f.latency, f.jitter)
    
    output += newline
    return output

#Produces a visual representation of the devices graph
#with pyvis, and opens it in a browser
def graph_topology(network):
    net = Network(height="700px", width="1200px")

    #devices
    for id in network:
        net.add_node(id, physics=False)

    #links
    for id in network:
        for p in network[id].ports:
            port = network[id].ports[p]
            if port.link != None:
                if port.link.latency != None and port.link.jitter != None:
                    net.add_edge(id, port.link.dstDevice, label= "%u, %u" % (port.link.latency, port.link.jitter), physics=False)
                else:
                    net.add_edge(id, port.link.dstDevice, physics=False)
            if port.host != None:
                if port.host.docker:
                    net.add_node(port.host.ips_list(), label=port.host.ips_list()+" [D]", shape="box", physics=False)
                else:
                    net.add_node(port.host.ips_list(), shape="box",physics=False)
                net.add_edge(id, port.host.ips_list(), physics=False)
    
    net.save_graph(GRAPH_FILE_NAME)

def take_timestamp(event):
    take_timestamp_at(event, time.time_ns())

def take_timestamp_at(event, timestamp):
    with open(os.path.expandvars("$CHIMA_ROOT/measurements/timestamps.txt"), "a") as file:
        file.write("%s:%u\n" %(event, timestamp) )

#From https://stackoverflow.com/questions/3232943/
def merge(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = merge(d.get(k, {}), v)
        else:
            d[k] = v
    return d