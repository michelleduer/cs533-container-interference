#!/usr/bin/env python3

"""
Run the Linpack benchmark for benchmarking the CPU and
graph the results to demonstrate if there may be any measureable
container interference across various experiments
"""

from subprocess import PIPE, Popen  # spawn processes with CLI commands
import pexpect                      # spawn, correspond with child processes
from numpy import float32, arange, mean as navg, asarray as narr  # quickly manipulate array types/statistics
from statistics import mean         # mean function
import matplotlib.pyplot as plt     # visual plotting of data
import seaborn as sns               # visual plotting of data


def barplot(averages: [float], plot_title: str, img_title: str):
    """
    Graph barplot from resulting benchmarking measuremnt(s)
    :param average: average value resulting from benchmarking GFlops
    :param plot_title: title of plot
    :param img_title: title of saved file
    """
    sns.set(style='ticks')
    x = arange(len(averages))
    ax = sns.barplot(x, gflops)
    ax.set(xlabel='Trial', ylabel='GFlops', title=plot_title, ylim=(0.0, 3.5))
    plt.show()

    img = './img/' + img_title
    plt.savefig(img)


def parse_results(logfile: str) -> float:
    """
    Grab the GFlops data from the log and store in data structure for graphing
    :param logfile: the logfile containing the benchmark results
    :return: return the gflop measuremnts
    """
    start = 30  # Line starting measurement table values (this line remains constant)
    results = []
    gflops_str = []

    # Reduce the logfile data to the benchmark measurements
    with open(logfile, 'r') as f:
        for count, line in enumerate(f):
            if 'Performance' in line:
                break
            if count > start:
                results.append(line.split("   "))
        f.close()

    # Reduce the benchmark measurements to the gflop values
    for meas in results[:-1]:
        gflops_str.append(meas[5])

    # Calculate average
    gflops = narr(gflops_str, dtype=float32)
    average = navg(gflops)

    return gflops, average


def benchmark_test(logfile: str, child: pexpect.spawnu, total_equations: int, leading_dimension: int, trials: int, alignment_value: int):
    """
    Set the parameters for Linpack and store the resulting benchmarked measurements into a file
    :param logfile: the file for storing results
    :param child: the child process that was spawned for running Linpack in Docker
    :param total_equations: the total number of linear equations that will be run
    :param leading_dimension: the array's leading dimension
    :param trials: the number of times the benchmark will be run
    :param alignment_value: is the memory alignment value (in kB)
    """
    fileout = open(logfile, 'w')

    child.logfile = fileout
    child.expect(':')
    child.send('\n')
    child.expect(':')
    child.send(total_equations)
    child.send('\n')
    child.expect(':')
    child.send(leading_dimension)
    child.send('\n')
    child.expect(':')
    child.send(trials)
    child.send('\n')
    child.expect(':')
    child.send(alignment_value)
    child.send('\n')
    child.expect(pexpect.EOF)

    child.close()
    return child.exitstatus, child.signalstatus


def run_docker(logfile: str, img: str, container_name: str):
    """
    Create and run a docker container with the provided image
    :param img: the image with which to run the container
    :param container_name: the container name
    """
    cmd = 'docker run --name ' + container_name + ' -it ' + img
    exit_status, signal_status = benchmark_test(logfile, pexpect.spawnu(cmd), total_equations,
                                                leading_dimension, trials, alignment_value)

    if exit_status != 0:
        raise ValueError(f'The Linpack process did not exit correctly. '
                         f'Exit Status: {exit_status} where expecting zero.')

    if signal_status is not None:
        raise ValueError(f'The Linpack process gave the incorrect status signal. '
                         f'Signal Status: {signal_status} where expecting None.')


def build_image(img: str):
    """
    Build a Linpack image from the Dockerfile
    :param img:
    """
    p = Popen(['docker', 'build', '-t', img, '.'], universal_newlines=True, stdout=PIPE)
    out, err = p.communicate()


if __name__ == '__main__':
    img = 'manta/linpack_img'
    container_name = 'test_container'
    logfile = 'results.log'
    averages = []

    total_equations = '100'
    leading_dimension = '100'
    trials = '5'
    alignment_value = '64'

    build_image(img)
    run_docker(logfile, img, container_name)
    averages.append(parse_results(logfile))
    plot_title = 'Experiment 1'
    img_title = 'test1'
    barplot(averages, plot_title, img_title)
