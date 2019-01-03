#!/usr/bin/python3

import sys
import subprocess

# Usage: 
#
#   test5.py host file [host file [host file [...]]]
#
# Spawns an instance of wrk for each host/file pair. Writes logs
# numbered according to the order in this list (1, 2, 3, ...).
# 
# Host should not have a trailing slash (/), and file should not
# have a leading slash (/).

benchmarks = [
    './wrk -d 60s http://192.168.1.135:81/1kb.dat > rawlogs/test5small.log', \
    './wrk -d 60s http://192.168.1.135:82/fedora29.iso > rawlogs/test5big.log', \
]

if __name__ == "__main__":
    procs = list()
    for command in benchmarks:
        procs.append(subprocess.Popen(command, shell=True))
    for  p in procs:
        p.wait()

