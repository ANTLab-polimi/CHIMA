#!/usr/bin/python3
from os import path, terminal_size
import time
import sys

prev = 0
pre_desc = None

arguments = "_".join(sys.argv[1:])

def split_time(begin, end):
    time = end - begin
    ns = time % 1000
    time /= 1000
    us = time % 1000
    time /= 1000
    ms = time % 1000
    time /= 1000
    s = time % 1000

    return s, ms, us, ns

with open('timestamps.txt') as f:
    with open('Times/times%u_%s.txt' %(int(time.time()), arguments ), 'w') as res:
        times = {}
        
        for line in f:
            parts = line.split(':')

            res.write(line)

            times[parts[0]] = int(parts[1])
        
        res.write("\n\n\n")

        s, ms, us, ns = split_time(times["PACKETS"], times["LATENCY"])
        res.write("Detection time:\t%us %ums %uus %uns\n" % (s, ms, us, ns))

        s, ms, us, ns = split_time(times["LATENCY"], times["REDEPLOYED"])
        res.write("Redeploy time:\t%us %ums %uus %uns\n" % (s, ms, us, ns))

        res.write("\n")

        s, ms, us, ns = split_time(times["PACKETS"], times["FIRST_PACKET"])
        res.write("Travel time of first packet:\t%us %ums %uus %uns\n" % (s, ms, us, ns))

        s, ms, us, ns = split_time(times["W_SWITCH"], times["SWITCH_OK"])
        res.write("Waiting for switches:\t%us %ums %uus %uns\n" % (s, ms, us, ns))

        s, ms, us, ns = split_time(times["W_CONTAINER"], times["CONTAINER_OK"])
        res.write("Waiting for containers:\t%us %ums %uus %uns\n" % (s, ms, us, ns))

        s, ms, us, ns = split_time(times["PATHS"], times["W_CONTAINER"])
        res.write("Installing paths:\t%us %ums %uus %uns\n" % (s, ms, us, ns))

        s, ms, us, ns = split_time(times["RULES"], times["REDEPLOYED"])
        res.write("Setting up triggers:\t%us %ums %uus %uns\n" % (s, ms, us, ns))
