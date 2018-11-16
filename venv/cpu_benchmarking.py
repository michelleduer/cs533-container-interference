#!/usr/bin/env python3

"""
PURPOSE: Run the Linpack benchmark for benchmarking the CPU
and graph the results to demonstrate if there may be any
measureable container interference across various experiments
"""

from subprocess import PIPE, Popen  # spawn processes with CLI commands
import pexpect  # respond to child processes


def store_measurements(child: spawn):
    """
    Set the parameters for Linpack and store the resulting benchmarked measurements into a file
    :param child: the child process that was spawned by creating the Docker container with Linpack
    """
    filename = 'results.log'
    fileout = open(filename, 'w')

    child.logfile = fileout
    child.expect(':')
    child.send('\n')
    child.expect(':')
    child.send(total_equations)
    child.send('\n')
    child.expect(':')
    child.send(array_dimensions)
    child.send('\n')
    child.expect(':')
    child.send(trials)
    child.send('\n')
    child.expect(':')
    child.send(alignment_value)
    child.send('\n')
    child.expect(pexpect.EOF)


def benchmark(total_equations: int, array_dimensions: int, trials: int, alignment_value: int):
    img = 'manta/linpack_img'
    container_name = 'test_container'

    # Build linpack image from Dockerfile
    p = Popen(['docker', 'build', '-t', img, '.'], universal_newlines=True, stdout=PIPE)
    out, err = p.communicate()

    # Create Docker container using the image
    cmd = 'docker run --name ' + container_name + ' -it ' + img
    store_measurements(pexpect.spawnu(cmd))


if __name__ == '__main__':
    total_equations = '100'
    array_dimensions = '100'
    trials = '5'
    alignment_value = '64'
    benchmark(total_equations, array_dimensions, trials, alignment_value)