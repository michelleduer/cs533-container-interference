#!/usr/bin/env python3

"""
Run the Linpack benchmark for benchmarking the CPU and
graph the results to demonstrate if there may be any measureable
container interference across various experiments
"""

from subprocess import PIPE, Popen  # spawn processes with CLI commands
import pexpect                      # spawn and correspond with child processes
from numpy import arange            # quickly manipulate array types/statistics
import matplotlib.pyplot as plt     # visual plotting of data
import seaborn as sns               # visual plotting of data


def clean_containers(baseline_name: str, baseline_tests: int):
    # Clean Baseline containers
    for b in range(baseline_tests):
        test = baseline_name + str(b + 1)
        cmd = 'docker stop ' + test
        pexpect.spawnu(cmd)
        cmd = 'docker rm ' + test
        pexpect.spawnu(cmd)


def baseline_tests(img: str, total_tests: int, test_name: str):
    """
    Implement baseline tests and save results in logs directory
    :param img: docker image
    :param total_tests: total number of tests
    :param test_name: base name of tests
    """
    for b in range(total_tests):
        test = test_name + str(b + 1)
        container_name = test
        logfile = './logs/' + test + '.log'

        if b == 0:
            print(f'baseline test ' + str(b + 1) + ': '
                  f'one container (2-cpu): Linpack')
            total_pinned_cpu = 2
            run_docker(logfile, img, container_name, True, total_pinned_cpu)
        elif b == 1:
            print(f'baseline test ' + str(b + 1) + ': '
                  f'one container (unrestricted): Linpack')
            run_docker(logfile, img, container_name, False)
        else:
            print(f'baseline test ' + str(b + 1) + ': '
                   f'no container (native 4-cpu): Linpack')
            cmd = './xlinpack_xeon64'
            total_equations = '1000'
            leading_dimension = '1000'
            trials = '50'
            alignment_value = '64'
            benchmark_test(logfile, pexpect.spawnu(cmd), total_equations, leading_dimension, trials, alignment_value)


def barplot(averages: [float], plot_title: str, img_title: str, total_tests: int):
    """
    Graph barplot from resulting benchmarking measuremnt(s)
    :param averages: average value resulting from benchmarking GFlops
    :param plot_title: title of plot
    :param img_title: title of saved file
    :param total_tests: total number of tests
    """
    sns.set(style='ticks')
    ax = sns.barplot(total_tests, averages)
    ax.set(xlabel='Experiments', ylabel='GFlops', title=plot_title, ylim=(0.0, 3.5))
    plt.show()

    img = './img/' + img_title
    plt.savefig(img)


def parse_results(logfile: str) -> float:
    """
    Grab the GFlops data from the log and store in data structure for graphing
    :param logfile: the logfile containing the benchmark results
    :return: return the gflop measuremnts
    """
    start = -1  # Line starting measurement table values
    average = 0.0

    # Reduce the logfile data to the benchmark measurements
    with open(logfile, 'r') as f:
        for count, line in enumerate(f):
            if 'Performance' in line:
                start = count + 3
            elif count == start:
                average = line.split()[3]
                break
        f.close()

    return average


def benchmark_test(logfile: str, child, total_equations: int, leading_dimension: int, trials: int, alignment_value: int):
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

    # Check for errors in running benchmark
    if child.exitstatus != 0:
        raise ValueError(f'The Linpack process did not exit correctly. '
                         f'Exit Status: {child.exitstatus} where expecting zero.')

    if child.signalstatus is not None:
        raise ValueError(f'The Linpack process gave the incorrect status signal. '
                         f'Signal Status: {child.signalstatus} where expecting None.')


def run_docker(logfile: str, img: str, container_name: str, pin: bool=False, total_pinned_cpu: int=2,
               total_equations: str='1000', leading_dimension: str='100', trials: str='50', alignment_value: str='64'):
    """
    Create and run a docker container with the provided image
    :param logfile: the file to save the linpack stdout 
    :param img: the image with which to run the container
    :param container_name: the container name
    :param pin: True if cpus need to be pinned, False otherwise
    :param total_pinned_cpu: the total number of cpus to pin
    :param total_equations: total number of linear equations to run
    :param leading_dimension: leading dimension of the matrix for the equations (minimum 1000)
    :param trials: total number of times the benchmark is run
    :param alignment_value: the alignment value for memory (minimum 64)
    """

    # Default command with no pinned CPUs
    cmd = 'docker run --name ' + container_name + ' -it ' + img

    # Format string for pinned CPUs
    if pin:
        cpu = ''
        for c in range(total_pinned_cpu):
            if c == total_pinned_cpu - 1:
                cpu += str(c)
            else:
                cpu += str(c) + ','
        cmd = 'docker run --name ' + container_name + ' -it --cpuset-cpus ' + cpu + ' ' + img

    benchmark_test(logfile, pexpect.spawnu(cmd), total_equations, leading_dimension, trials, alignment_value)


def build_image(img: str):
    """
    Build a Linpack image from the Dockerfile
    :param img: name of image
    """
    p = Popen(['docker', 'build', '-t', img, '.'], universal_newlines=True, stdout=PIPE)
    out, err = p.communicate()


if __name__ == '__main__':

    # Build the Linpack image
    img = 'manta/linpack_img'
    print(f'creating ' + img + ' image...')
    build_image(img)

    # Run test cases
    baseline_total_tests = 3
    baseline_test_name = 'baseline'
    print(f'running ' + str(baseline_total_tests) + ' baseline tests...')
    baseline_tests(img, baseline_total_tests, baseline_test_name)

    """
    print('parsing results...')
    parse_results('results.log')
    """

    print('stopping/removing tests...')
    clean_containers(baseline_test_name, baseline_total_tests)
    print('Done!')
