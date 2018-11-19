#!/usr/bin/env python3

"""
Run the Linpack benchmark for benchmarking the CPU and
graph the results to demonstrate if there may be any measureable
container interference across various experiments
"""

from subprocess import PIPE, Popen  # spawn processes with CLI commands
import pexpect                      # spawn and correspond with child processes
import matplotlib.pyplot as plt     # visual plotting of data
import seaborn as sns               # visual plotting of data
from threading import Thread as tr  # threading
# resource: https://www.quantstart.com/articles/Parallelising-Python-with-Threading-and-Multiprocessing
from os import listdir              # work with file directory
from pandas import DataFrame as df  # use dataframes for plotting

def parse_tests():
    """
    Parse and graph baseline, single and multi tests
    """
    baseline_gflops = []
    single_gflops = []
    multi_gflops = []

    files = sorted(listdir('./logs/'))
    for f in files:
        gflop = float(parse_file(f))
        if gflop > 0:
            if 'baseline' in f:
                baseline_gflops.append(gflop)
            elif 'single' in f:
                single_gflops.append(gflop)
            elif 'multi' in f:
                multi_gflops.append(gflop)

    # Plot barplots
    baseline_legend = ['cL/cL res', 'cL unr', 'nL', 'cL</cL res']
    single_legend = ['']
    multi_legend = ['']
    barplot(baseline_gflops, len(baseline_gflops), baseline_legend, plot_title='Baseline Tests', img_title='baseline_tests')
    barplot(single_gflops, len(single_gflops), single_legend, plot_title='Single Core Tests', img_title='single_tests')
    barplot(multi_gflops, len(multi_gflops), multi_legend, plot_title='Multi-Core Tests', img_title='multi_tests')


def single_tests(img: str, stress_img: str, total_tests: int, test_name: str, threads: int=2):
    """
    Tests that run on a single container
    :param img: a docker linpack image
    :param stress_img: a docker stress image
    :param total_tests: the total number of tests
    :param test_name: the base test name
    :param threads: the total number of threads
    :return the names of tests
    """
    jobs = []
    names = []

    for b in range(total_tests):
        if b == 0:
            print(f'{str(b + 1)}: single container (4-cpu): Linpack, Linpack')
            for i in range(threads):
                name = test_name + str(b + 1) + '-' + str(i + 1)
                logfile = './logs/' + name + '.log'
                if i == 0:
                    name = test_name + str(b + 1) + '-' + str(i + 1)
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=4, start=0))
                else:
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=4, start=0))
                jobs.append(thread)
                names.append(name)
        elif b == 1:
            print(f'{str(b + 1)}: single container (2-cpu): Linpack, Linpack')
            for i in range(threads):
                name = test_name + str(b + 1) + '-' + str(i + 1)
                logfile = './logs/' + name + '.log'
                if i == 0:
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=2, start=0))
                else:
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=2, start=0))
                jobs.append(thread)
                names.append(name)
        elif b == 2:
            print(f'{str(b + 1)}: single container (4-cpu): Linpack, stress')
            for i in range(threads):
                name = test_name + str(b + 1) + '-' + str(i + 1)
                logfile = './logs/' + name + '.log'
                if i == 0:
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=2, start=0))
                    names.append(name)
                elif i == 1:
                    thread = tr(target=run_docker(logfile, stress_img, name, False, total_pinned_cpu=2, start=0, stress=True))
                jobs.append(thread)
        else:
            print(f'{str(b + 1)}: single container (2-cpu): Linpack, stress')
            for i in range(threads):
                name = test_name + str(b + 1) + '-' + str(i + 1)
                logfile = './logs/' + name + '.log'
                if i == 0:
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=2, start=0))
                    names.append(name)
                elif i == 1:
                    thread = tr(target=run_docker(logfile, stress_img, name, False, total_pinned_cpu=2, start=0, stress=True))
                jobs.append(thread)

        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        jobs.clear()

    return names


def multi_tests(img: str, stress_img: str, total_tests: int, test_name: str, threads: int=2):
    """
    Tests that run on 2 or more containers
    :param img: a docker linpack image
    :param stress_img: a docker stress image
    :param total_tests: the total number of tests
    :param test_name: the base test name
    :param threads: total number of threads
    :return the names of tests
    """
    jobs = []
    names = []

    for b in range(total_tests):
        if b == 0:
            print(f'{str(b + 1)}: two container (unrestricted): Linpack, Linpack')
            for i in range(threads):
                name = test_name + str(b + 1) + '-' + str(i + 1)
                logfile = './logs/' + name + '.log'
                thread = tr(target=run_docker(logfile, img, name, False))
                jobs.append(thread)
                names.append(name)
        elif b == 1:
            print(f'{str(b + 1)}: two container (2-cpu): Linpack, Linpack')
            for i in range(threads):
                name = test_name + str(b + 1) + '-' + str(i + 1)
                logfile = './logs/' + name + '.log'
                if i == 0:
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=2, start=0))
                else:
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=2, start=2))
                jobs.append(thread)
                names.append(name)
        elif b == 2:
            print(f'{str(b + 1)}: two container (unrestricted): Linpack, stress (testing 2-cpu)')
            for i in range(threads):
                name = test_name + str(b + 1) + '-' + str(i + 1)
                logfile = './logs/' + name + '.log'
                if i == 0:
                    thread = tr(target=run_docker(logfile, img, name, False))
                elif i == 1:
                    thread = tr(target=run_docker(logfile, stress_img, name, False, total_pinned_cpu=0, start=0, stress=True))
                names.append(name)
                jobs.append(thread)
        elif b == 3:
            print(f'{str(b + 1)}: two container (2-cpu): Linpack, stress (testing 2-cpu)')
            for i in range(threads):
                name = test_name + str(b + 1) + '-' + str(i + 1)
                logfile = './logs/' + name + '.log'
                if i == 0:
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=2, start=0))
                elif i == 1:
                    thread = tr(target=run_docker(logfile, stress_img, name, True, total_pinned_cpu=2, start=2, stress=True))
                jobs.append(thread)
                names.append(name)
        elif b == 4:
            print(f'{str(b + 1)}: two container (unrestricted): Linpack (<100%), Linpack(100%)')
            for i in range(threads):
                name = test_name + str(b + 1) + '-' + str(i + 1)
                logfile = './logs/' + name + '.log'
                if i == 0:
                    thread = tr(target=run_docker(logfile, img, name, False, total_pinned_cpu=0, stress=False,
                                                  total_equations='500'))
                elif i == 1:
                    thread = tr(target=run_docker(logfile, img, name, False))
                jobs.append(thread)
                names.append(name)
        elif b == 5:
            print(f'{str(b + 1)}: two container (2-cpu): Linpack (<100%), Linpack (100%)')
            for i in range(threads):
                name = test_name + str(b + 1) + '-' + str(i + 1)
                logfile = './logs/' + name + '.log'
                if i == 0:
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=2, start=0, stress=False,
                                                  total_equations='500'))
                elif i == 1:
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=2, start=2))
                jobs.append(thread)
                names.append(name)
        else:
            print(f'{str(b + 1)}: one container (2-cpu) and native: Linpack (<100%), native (100%)')
            for i in range(threads):
                name = test_name + str(b + 1) + '-' + str(i + 1)
                logfile = './logs/' + name + '.log'
                if i == 0:
                    thread = tr(target=run_docker(logfile, img, name, True, total_pinned_cpu=2, start=0, stress=False,
                                                  total_equations='500'))
                elif i == 1:
                    cmd = './xlinpack_xeon64'
                    total_equations = '1000'
                    leading_dimension = '1000'
                    trials = '50'
                    alignment_value = '64'
                    thread = tr(target=benchmark_linpack(logfile, pexpect.spawnu(cmd), total_equations,
                                                         leading_dimension, trials, alignment_value))
                jobs.append(thread)
                names.append(name)

        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        jobs.clear()

    return names


def clean_containers(tests: [str]):
    """
    Stop and remove containers that have been tested
    :param tests: list of test names
    """
    for test in tests:
        p = Popen(['docker', 'stop', test], universal_newlines=True, stdout=PIPE)
        p = Popen(['docker', 'rm', test], universal_newlines=True, stdout=PIPE)


def baseline_tests(img: str, total_tests: int, test_name: str):
    """
    Implement baseline tests and save results in logs directory
    :param img: docker image
    :param total_tests: total number of tests
    :param test_name: base name of tests
    :return the names of tests
    """
    names = []

    for b in range(total_tests):
        name = test_name + str(b + 1)
        logfile = './logs/' + name + '.log'

        if b == 0:
            print(f'{str(b + 1)}: one container (2-cpu): Linpack')
            run_docker(logfile, img, name, True, total_pinned_cpu=2, start=0)
            names.append(name)
        elif b == 1:
            print(f'{str(b + 1)}: one container (unrestricted): Linpack')
            run_docker(logfile, img, name, False)
            names.append(name)
        elif b == 2:
            print(f'{str(b + 1)}: no container (native 4-cpu): Linpack')
            cmd = './xlinpack_xeon64'
            total_equations = '1000'
            leading_dimension = '1000'
            trials = '50'
            alignment_value = '64'
            benchmark_linpack(logfile, pexpect.spawnu(cmd), total_equations, leading_dimension, trials, alignment_value)
        else:
            print(f'{str(b + 1)}: one container (2-cpu): Linpack (<200%)')
            total_equations = '500'
            leading_dimension = '1000'
            trials = '50'
            alignment_value = '64'
            run_docker(logfile, img, name, True, total_pinned_cpu=2, start=0, stress=False, total_equations='500')

    return names


def barplot(gflops: [float], total_tests: int, legend: [str], plot_title: str, img_title: str):
    """
    Graph barplot from resulting benchmarking measuremnt(s)
    :param gflops: average value resulting from benchmarking GFlops
    :param total_tests: total number of tests
    :param legend: legend values
    :param plot_title: title of plot
    :param img_title: title of saved file
    """
    sns.set(style='ticks')
    test_count = []

    # Check for case where there is nothing to plot
    if total_tests == 0:
        return

    for t in range(1, total_tests + 1):
        test_count.append(t)

    ax = sns.barplot(test_count, gflops)
    #ax.set(xlabel='Experiments', ylabel='Average GFlops per 50 Trials', title=plot_title, ylim=(0.0, 3.5)) # TODO use y-lim?
    ax.set(xlabel='Experiments', ylabel='Average GFlops per 50 Trials', title=plot_title)

    # Set legend outside of plot (specfically below)
    # resource: https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot/4701285#4701285
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    # Save plot image
    img = './img/' + img_title
    plt.savefig(img)

    # Display plot
    plt.show()


def parse_file(logfile: str) -> float:
    """
    Grab the GFlops data from the log and store in data structure for graphing
    :param logfile: the logfile containing the benchmark results
    :return: return the gflop measuremnts
    """
    start = -1  # Line starting measurement table values
    average = 0.0

    # Reduce the logfile data to the benchmark measurements
    with open('./logs/' + logfile, 'r') as f:
        for count, line in enumerate(f):
            """ # TODO delete
            if count == 0 and 'stress' in line:
                return average
                """
            if 'Performance' in line:
                start = count + 3
            elif count == start:
                average = line.split()[3]
                break
        f.close()

    return average


def benchmark_linpack(logfile: str, child: pexpect.spawnu, total_equations: int, leading_dimension: int, trials: int, alignment_value: int):
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


def run_docker(logfile: str, img: str, container_name: str, pin: bool=False, total_pinned_cpu: int=2, start: int=0,
               stress: bool=False, total_equations: str='1000', leading_dimension: str='100', trials: str='50',
               alignment_value: str='64'):
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
        for c in range(start, start + total_pinned_cpu):
            if c == start + total_pinned_cpu - 1:
                cpu += str(c)
            else:
                cpu += str(c) + ','
        cmd = 'docker run --name ' + container_name + ' -it --cpuset-cpus ' + cpu + ' ' + img

    if stress:
        pexpect.spawnu(cmd)
        """ TODO: try with closing  
        fileout = open(logfile, 'w')
        child.logfile = fileout
        child.expect(pexpect.EOF)
        child.close(force=True)
        """
    else:
        benchmark_linpack(logfile, pexpect.spawnu(cmd), total_equations, leading_dimension, trials, alignment_value)


def build_image(img: str, dockerfile: str):
    """
    Build a Linpack image from the Dockerfile
    :param img: name of image
    """
    p = Popen(['docker', 'build', '-f', dockerfile, '-t', img, '.'], universal_newlines=True, stdout=PIPE)
    out, err = p.communicate()


if __name__ == '__main__':

    # Build the Linpack image
    img = 'manta/linpack'
    dockerfile = 'Dockerfile.lp'
    print(f'\ncreating ' + img + ' image...')
    build_image(img, dockerfile)

    # Build the Linpack image
    stress_img = 'manta/stress'
    dockerfile = 'Dockerfile.st'
    print(f'creating ' + stress_img + ' image...')
    build_image(stress_img, dockerfile)

    # Baseline Tests
    baseline_total_tests = 4
    name = 'baseline'
    print(f'\nrunning ' + str(baseline_total_tests) + ' baseline tests...')
    baseline_names = baseline_tests(img, baseline_total_tests, name)

    # Multiple Core Tests
    multi_total_tests = 6
    name = 'multi'
    print(f'\nrunning ' + str(multi_total_tests) + ' multi-container tests...')
    multi_names = multi_tests(img, stress_img, multi_total_tests, name)

    # Single Core Tests
    single_total_tests = 4
    name = 'single'
    print(f'\nrunning ' + str(single_total_tests) + ' single-container tests...')
    single_names = single_tests(img, stress_img, single_total_tests, name)

    print('\nparsing results...')
    parse_tests()

    print('\nstopping/removing tests...')
    clean_containers(baseline_names)
    clean_containers(multi_names)
    clean_containers(single_names)

    print('\nDone!')
