from bcc import BPF
import os
import time, datetime
import logging
from prometheus_client import start_http_server, Gauge

from triggers import *
from components import *
from metrics import *
from deployment import redeploy

DEBUG = True
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

class INT_collector(object):
    def __init__ (self, filename = "collector/collector.c", max_int_hop = 12, int_dst_port = 54321, shr_ewma = 4, n_switches = 100, polling_interval = 0.1):
        self.FILENAME = filename
        self.MAX_INT_HOP = max_int_hop
        self.INT_DST_PORT = int_dst_port
        self.SHR_EWMA = shr_ewma
        self.POLLING_INTERVAL = polling_interval
        self.HASHMAP_LINK_SIZE = n_switches*(n_switches - 1)
        self.gauges = {}

        self.bpf = BPF(src_file=filename, debug=0,
        cflags=["-w",
                "-D_MAX_INT_HOP=%s" % self.MAX_INT_HOP,
                "-D_INT_DST_PORT=%s" % self.INT_DST_PORT,
                "-D_SHR_EWMA=%s" % self.SHR_EWMA,
                "-D_HASHMAP_LINK_SIZE=%s" % self.HASHMAP_LINK_SIZE])

        self.link_metrics_map = self.bpf["link_metrics_map"]

        self.prev_link_fed_metrics = dict()
        self.fn = self.bpf.load_func("collector", BPF.XDP)

    @staticmethod
    def fix_overflowed_value(val):
        UINT32_MAX = 0xFFFFFFFF
        return val if val >= 0 else val + UINT32_MAX + 1

    def attach_bpf_program(self, device, flags=0):
        self.device = device
        self.bpf.attach_xdp(device, self.fn, flags)

    def remove_bpf_program(self, flags=0):
        self.bpf.remove_xdp(self.device, flags)

    def send_metrics(self, network, int_funcs):
        #Prometheus exporter
        start_http_server(8000)
        gauges = self.gauges

        #logging.info("POLLING_INTERVAL is %d" % (self.POLLING_INTERVAL))
        #logging.info("Printing stats, hit CTRL+C to stop")
        while True:
            try:
                current_time = time.time()
                wait_time = self.POLLING_INTERVAL - current_time % self.POLLING_INTERVAL
                time.sleep(wait_time)

                for link_key, link_metrics in self.link_metrics_map.items():
                    label = str(link_key.switch_id_1)+"_"+str(link_key.switch_id_2)
                    latency_label = "l_" + label
                    jitter_label = "j_" + label
                    
                    if latency_label not in gauges:
                        gauges[latency_label] = Gauge(latency_label, 'Latency of the link')
                        # logging.debug("New gauge: LINK_KEY = (%u,%u) LATENCY = %u" \
                        # % (link_key.switch_id_1, link_key.switch_id_2, link_metrics.latency))

                    if jitter_label not in gauges:
                        gauges[jitter_label] = Gauge(jitter_label, 'Jitter of the link')
                        # logging.debug("New gauge: LINK_KEY = (%u,%u) JITTER = %u" \
                        # % (link_key.switch_id_1, link_key.switch_id_2, link_metrics.jitter))

                    gauges[latency_label].set(link_metrics.latency)
                    gauges[jitter_label].set(link_metrics.jitter)

                    #Update latency in the network model
                    ids = [link_key.switch_id_1, link_key.switch_id_2]
                    assignMetrics(link_metrics.latency, link_metrics.jitter, ids, network, int_funcs)
                    if ids[1] >= 100:
                        collected_metrics[ frozenset( [ids[1]] ) ] = Metrics(link_metrics.latency, link_metrics.jitter)
                    else:
                        collected_metrics[frozenset(ids)] = Metrics(link_metrics.latency, link_metrics.jitter)

                    # logging.debug("LINK_KEY = (%u,%u) LATENCY = %u" \
                    # % (link_key.switch_id_1, link_key.switch_id_2, link_metrics.latency))
                
                #Perform a check to see if any trigger was exceeded
                deployment = check_triggers(triggers)

                if deployment != None:
                        redeploy(deployment.depFile, deployment.next)
            except KeyboardInterrupt:
                logging.info("Removing filter from device")
                self.remove_bpf_program()
                break   
