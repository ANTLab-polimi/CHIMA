#!/usr/bin/python3
from mininet.net import Containernet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.bmv2 import ONOSBmv2Switch, P4DockerHost, P4Host
from mininet.link import Intf, TCLink
import os
import sys
import time
setLogLevel('info')

CHAIN_LEN = 2
SWITCHES_NUM = CHAIN_LEN * 2 + 1

TIMESTAMPS_FILE = os.path.expandvars("$CHIMA_ROOT/measurements/timestamps.txt")
def take_timestamp(event):
    with open(TIMESTAMPS_FILE, "a") as file:
        file.write("%s:%u\n" %(event, time.time_ns()) )

#This extension of Containernet's CLI allows the delay on the link to be changed
class DelayCLI(CLI):
    def do_delay(self, line):
        global delay_link
        delay_link.intf1.config(delay = line)
        delay_link.intf2.config(delay = line)
        take_timestamp("DELAY_CHANGED")
        print("")

class NormalP4Switch(ONOSBmv2Switch):
    def __init__(self, name, **kwargs):
        ONOSBmv2Switch.__init__(self, name, **kwargs)
        self.netcfg = False

net = Containernet(controller=RemoteController, switch=NormalP4Switch)

info('*** Creating veths\n')
os.system("../../common/veth.sh")

info('*** Adding controller\n')
net.addController(RemoteController('c0', '127.0.0.1'))

info('*** Adding switches\n')

switches={}
for i in range(0,SWITCHES_NUM):
    switches[i] = net.addSwitch('s%u%u' % (i,i), loglevel="info", pipeconf="org.onosproject.pipelines.int")

info('*** Adding hosts\n')

hosts={}
for i in range(1,SWITCHES_NUM):
    hosts[i] = net.addDocker('d%u' % i, cls=P4DockerHost, ip='10.0.0.10%u/24' % i, mac="00:00:00:00:00:0%u" % i, dimage="erap320:dind")
    hosts[i].start()

info('*** Creating links\n')
collectorIntf = Intf( 'veth_2', node=net.nameToNode[ "s00" ] )
delay_link = net.addLink(switches[0], switches[1], cls=TCLink, delay="1ms")
net.addLink(hosts[1], switches[1])
net.addLink(switches[0], switches[2])
net.addLink(hosts[2], switches[2])
for i in range(3, SWITCHES_NUM):
    net.addLink(switches[i-2], switches[i])
    net.addLink(hosts[i], switches[i])
    

info('*** Starting network\n')

net.start()

info('*** Disable checksum offloading on all hosts\n')
# If checksum offloading is active on these interfaces
# checksums will be wrong, and packets won't be forwarded
# between network namespaces
for docker in net.hosts:
    docker.config()

info('*** Adding switches to ONOS\n')
for switch in net.switches:
    os.system(os.path.expandvars("$ONOS_ROOT/tools/package/runtime/bin/onos-netcfg localhost /tmp/bmv2-"+switch.name+"-netcfg.json"))

info('*** Creating mirroring session\n')
# The mirroring session is needed to clone packets used as a base
# for the INT report packets sent to the collector
# INT clones packets with mirroring session 500

for i in range(0, SWITCHES_NUM):
    os.system('echo "mirroring_add 500 1" | simple_switch_CLI --thrift-port $(cat /tmp/bmv2-s%u%u-thrift-port)' % (i,i))

info('*** Adding collector information to ONOS\n')
os.system(os.path.expandvars('$ONOS_ROOT/tools/package/runtime/bin/onos-netcfg localhost ../../common/collector.json'))

info('*** Running CLI\n')
DelayCLI(net)
info('*** Stopping network\n')
net.stop()

info('*** Cleaning veths\n')
os.system("../../common/del_veth.sh")
