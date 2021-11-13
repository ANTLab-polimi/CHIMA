from metrics import *
from utils import take_timestamp

class Trigger:
    def __init__(self, deployment) -> None:
        self.deployment = deployment
        self.endtoend = False
        self.max_latency = None
        self.min_latency = None
        self.metrics = []
        self.l_max = None
        self.j_max = None
        self.v_max = None

triggers = {}

def compute_trigger(t):
    total_lat = 0
    total_jitter = 0

    #Make sums
    for m in t.metrics:
        if m not in collected_metrics:
            return (0,0,0)
        else:
            total_lat += collected_metrics[m].latency
            total_jitter += collected_metrics[m].jitter
    
    if t.endtoend:
        total_lat *= 2
        total_jitter *= 2

    if t.max_latency == None:
        t.max_latency = total_lat
    else:
        t.max_latency = max(t.max_latency, total_lat)

    if t.min_latency == None:
        t.min_latency = total_lat
    else:
        t.min_latency = min(t.min_latency, total_lat)

    lat_variation = abs(t.max_latency - t.min_latency)
    t.last_latency = total_lat
    
    return (total_lat, total_jitter, lat_variation)

def check_triggers(triggers):
    for fun_id in triggers:
        t = triggers[fun_id]
        
        (total_lat, total_jitter, lat_variation) = compute_trigger(t)
        if total_lat == 0 and total_jitter == 0:
            return

        react = False
        if t.l_max != None and total_lat > t.l_max:
            take_timestamp("LATENCY")
            print("TRIGGER! Latency %u>%u" % (total_lat, t.l_max))
            react = True
            
        if t.j_max != None and abs(total_jitter) > t.j_max:
            take_timestamp("JITTER")
            print("TRIGGER! Jitter %d>%d" % (total_jitter, t.j_max))
            react = True
        
        if t.j_max != None and total_jitter > t.j_max:
            take_timestamp("VARIATION")
            print("TRIGGER! Variation %u>%u" % (lat_variation, t.v_max))
            react = True
        
        if react and t.deployment.next != None:
            return t.deployment
    
    return None

def show_triggers(triggers):
    for fun_id in triggers:
        t = triggers[fun_id]
        
        (total_lat, total_jitter, lat_variation) = compute_trigger(t)             
            
        print("trigger %u: LAT %u(%u) JIT %d(%d) VAR %u(%u)" % (fun_id, total_lat, 0 if t.l_max == None else t.l_max, abs(total_jitter), 0 if t.j_max == None else t.j_max, lat_variation, 0 if t.v_max == None else t.v_max) )