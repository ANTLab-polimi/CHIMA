from bcc import BPF
import time
import logging
from pyroute2 import IPRoute, IPDB
import socket
from ctypes import *

from mpls import *

ipr = IPRoute()
ipdb = IPDB(nl=ipr)

DEBUG = True
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

class MPLS_encapsulator(object):
    def __init__ (self, maps_size, mpls_stack_size=8, filename = "encapsulator/encapsulator.c"):
        self.bpf = BPF(src_file=filename, debug=0,
        cflags=["-w",
                "-D_MAPS_SIZE=%s" % maps_size,
                "-D_MAX_MPLS_STACK_SIZE=%s" % mpls_stack_size])

        self.dst_stacks_map = self.bpf["dst_stacks_map"]
        self.fn = self.bpf.load_func("encapsulator", BPF.SCHED_CLS)
        self.interface = None
        print("BPF loaded...")

    def attach_bpf_program(self, device, flags=0):
        ifc = ipdb.interfaces[device]
        ipr.tc("add", "sfq", ifc.index, "1:")
        ipr.tc("add-filter", "bpf", ifc.index, ":1", fd=self.fn.fd, name=self.fn.name, parent="1:", action="ok", classid=1)
        self.interface = device

    def remove_bpf_program(self, flags=0):
        if self.interface != None:
            ifc = ipdb.interfaces[self.interface]
            ipr.tc("del", "sfq", ifc.index, "1:")
            self.interface = None

    def map_inject(self, source, destination, labels: mpls_stack):
        temp_key = self.dst_stacks_map.Key()
        temp_leaf = self.dst_stacks_map.Leaf()

        temp_key.src = c_uint(socket.htonl(source))
        temp_key.dst = c_uint(socket.htonl(destination))
        for i in range(0, labels.size):
            temp_leaf.stack[i].value = labels.stack[i]

        temp_leaf.size = labels.size

        self.dst_stacks_map[temp_key] = temp_leaf

    def map_remove(self, source, destination):
        temp_key = self.dst_stacks_map.Key()
        temp_key.src = c_uint(socket.htonl(source))
        temp_key.dst = c_uint(socket.htonl(destination))

        array = (type(temp_key) * 1)()
        array[0] = temp_key
        try:
            self.dst_stacks_map.items_delete_batch( array )
        except:
            pass

    def manage_runtime(self):
        while True:
            try:
                # self.bpf.trace_print()
                time.sleep(60)
            except KeyboardInterrupt:
                self.remove_bpf_program(self.interface)
                logging.info("Removing devices")
                break
