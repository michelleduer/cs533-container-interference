#!/usr/bin/python3

import sys
import subprocess

# This file contains a function to run multiple instances of a command
# and a script that runs this from the command-line for basic usage.
#
# Script usage:
#
#   This script runs one or many instances of a given command, in parallel.
#
#   Usage:
#   
#     run n command [args...]
#
#     n - number of instance of the command to spawn in parallel.
#     command - the command to be run, with any arguments, as a single string.
#     args - any arguments to the command.
#
#   Example:
#
#     run 4 iperf3 -c localhost -t 60
#
#   Multiple invocations with different arguments:
#
#     There are use cases that require different arguments for each invocation
#     of the given command, and this is more easily supported using the full
#     power of Python functions. To use this functionality, you'll have to use
#     the Python function instead.
#
# Python function usage:
#
#   runcmd(n, command, shell=False)
#
#     n - same as above.
#     command - either a valid argument to subprocess.run's arg parameter
#       (a single string or an array of strings) or a function of the form
#       f(i) that accepts an index i and returns either of the above.
#       Indexes passed to the function will range from 1 to n (inclusive).
#     shell - optional. Passed to subprocess.Popen.
#     
#
#   Example:
#
#     def logeach(i):
#       return ["mycmd", "--logfile", "logfile_{}".format(i)]
#
#     runcmd(4, logeach)

def runcmd(n, command, shell=False):
  if type(n) is not int or n < 1:
    raise ValueError("n should be an integer no less than 1.")

  # List of processes to wait for.
  processes = list()

  if callable(command):
    # command is a function.
    for i in range(1, (n+1)):
      arg = command(i)
      processes.append(subprocess.Popen(arg, shell))

  else:
    # command is a string.
    for i in range(1, (n+1)):
      processes.append(subprocess.Popen(command, shell))
  
  # Now wait for the open processes to complete.
  for p in processes:
      p.wait()

if __name__ == "__main__":
  # Script usage.

  runcmd(int(sys.argv[1]), sys.argv[2:])
  sys.exit()

