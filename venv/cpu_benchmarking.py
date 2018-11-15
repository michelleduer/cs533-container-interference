#!/usr/bin/env python3

"""
PURPOSE: Run the Linpack benchmark for benchmarking the CPU
and graph the results to demonstrate if there may be any 
measureable container interference across various experiments
"""

from subprocess import PIPE, Popen  # spawn processes with CLI commands


def benchmark():
    img = 'manta/linpack_img'
    container_name = 'test_container'

    p = Popen(['docker', 'build', '-t', img, '.'], universal_newlines=True, stdout=PIPE)
    out, err = p.communicate()
    print(f'image built:\n {out}')
    
    p = Popen(['docker', 'run', '--name', container_name, '-it', img], universal_newlines=True, stdout=PIPE)

    if p.returncode is None:
        for line in p.stdout:
            line = line.rstrip()
            print(line)
    


if __name__ == '__main__':
    benchmark()