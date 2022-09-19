#!/usr/bin/python3
import socket
import sys
import time
import os

def take_timestamp(event):
    with open( os.path.expandvars("$CHIMA_ROOT/measurements/Times/timestamps.txt"), "a") as file:
        file.write("%s:%u\n" %(event, time.time_ns()) )

ip = "0.0.0.0"
port = 12345

c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.settimeout(1)

interval = 0.1
if len(sys.argv) > 1:
    interval = float(sys.argv[1])
    print("Packet interval set to %f seconds" % interval)

counter = 0
take_timestamp("PACKETS")
msg = b"hello! "+str(counter).encode("utf-8")
print(msg)
c.sendto(msg, ("10.0.0.2", 12345))
try:
    response, func_addr = c.recvfrom(65535)
    take_timestamp("FIRST_PACKET")
    print(response)
except socket.timeout as e:
    pass

counter += 1
time.sleep(0.1)

while(True):
    #send to second function
    msg = b"hello! "+str(counter).encode("utf-8")
    print(msg)
    c.sendto(msg, ("10.0.0.2", 12345))
    try:
        response, func_addr = c.recvfrom(65535)
        print(response)
    except socket.timeout as e:
        pass

    counter += 1
    time.sleep(0.1)
