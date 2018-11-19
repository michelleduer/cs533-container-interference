#!/usr/bin/python3

import sys
import subprocess
from runcmd import runcmd

# Usages: 
#
#   test2.py n -c host bandwidth
#   test2.py n -s
#
# n is the number of invocations to perform.
# host is the target where the server is located, e.g. 
#   localhost or some IP address.
# bandwidth is the amount of bandwidth to use, as specified
#   to iperf3 for the -b option. (This will be passed to -b.)
#
# If -c is specified, then iperf3 will run in client mode.
# If -s is specified, then iperf3 will run in server mode, using
#   the -1 option to exit after 1 test.
#
# The ports used will start at 5201 and go up from there as needed,
# e.g. n=3 will use 5201 through 5203.
#
# Note: the server will run natively; the client will run in Docker.

host = None
log_directory = 'rawlogs'
client_logfile_format = '{}/client{{}}.log'.format(log_directory)
server_logfile_format = '{}/server{{}}.log'.format(log_directory)
time = 60
base_port = 5201
container_name_format = 'iperf3_{}'

def client_getcmd(i):
    port = base_port + i - 1
    return ['docker', 'run',
            '--name', container_name_format.format(i),
            '-p', '{}:{}'.format(port, port),
            'iperf3', # image name
            'iperf3', # start of the command to run in the container
            '-c', host, '-t', str(time), 
            # '--logfile', client_logfile_format.format(i),
            '-p', str(port),
            '-b', sys.argv[4]]

def server_getcmd(i):
    return ['iperf3', '-s', '-1', 
            '--logfile', server_logfile_format.format(i), 
            '-p', str(base_port + i - 1)]

def copy_logs(n, log_format):
    for i in range(1, n+1):
        cname = container_name_format.format(i)
        logfile = log_format.format(i)
        command = "docker logs {} &> {}".format(cname, logfile)
        subprocess.run(command, shell=True)

def remove_docker_containers(n):
    for i in range(1, n+1):
        cname = container_name_format.format(i)
        command = "docker container rm {}".format(cname)
        subprocess.run(command, shell=True)

if __name__ == "__main__":
    n = int(sys.argv[1])

    # Delete existing raw logs.
    subprocess.run("rm {}/*.log".format(log_directory), shell=True)

    if sys.argv[2] == '-c':
      # Client mode.

      # Start Docker containers.
      host = sys.argv[3]
      runcmd(n, client_getcmd)

      # Copy logfiles.
      copy_logs(n, client_logfile_format)

      # Remove Docker containers.
      remove_docker_containers(n)
    elif sys.argv[2] == '-s':
      # Server mode.
      runcmd(n, server_getcmd)
    else:
      raise ValueError("The second argument must be either -c or -s.")
