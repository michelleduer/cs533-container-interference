#!/usr/bin/env python3

import matplotlib.pyplot as plt     # visual plotting of data
import seaborn as sns               # visual plotting of data
from os import listdir              # work with file directory
from pandas import pandas as pd     # handling data
import csv                          # create CSVs from data


def barplot(filename: str, x_label: str, y_label: str, img_title: str):
    """
    Graph barplot from resulting benchmarking measuremnt(s)
    :param filename: file containing data
    :param x_label: x label's name
    :param y_label: y label's name
    :param img_title: title of saved file
    """
    sns.set(style='whitegrid')
    df = pd.read_csv('./csv/' + filename)
    ax = sns.barplot(data=df)
    ax.set(xlabel=x_label, ylabel=y_label)

    # Save plot image
    img = './graph/' + img_title
    plt.savefig(img)

    # Display plot
    plt.show()


def create_csv(filename: str, header: [str], data: [float]):
    """
    Creates CSVs from the data for later use with pandas dataframes
    :param filename: the new csv filename
    :param header: the data headers
    :param data: the data values
    """
    with open('./csv/' + filename, 'w', newline='') as f:
        wr = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE)
        wr.writerow(header)
        wr.writerow(data)
    f.close()


def parse_tests():
    """
    Parse and graph baseline and other tests
    """
    baseline_gflops = []
    reduced_gflops = []
    microservice_gflops = []
    multi_gflops = []
    lv_ls_gflops = []

    files = sorted(listdir('./graph_data/'))
    for f in files:
        print(f)
        gflop = float(parse_file(f))
        if gflop > 0:
            if 'baseline' in f:
                baseline_gflops.append(gflop)
            elif 'reduced' in f:
                reduced_gflops.append(gflop)
            elif 'microservice' in f:
                microservice_gflops.append(gflop)
            elif 'multi' in f:
                multi_gflops.append(gflop)
            elif 'lv' in f:
                lv_ls_gflops.append(gflop)

    # Plot barplots
    baseline_legend = ['Lr2', 'L', 'nL', 'L<r2']
    reduced_legend = ['L<r base', ' L< ', 'L ', ' L<r2 ', 'Lr2 ', ' L<r2', 'nL ', '  L<r2', 'L<r2 ', ' L<', 'L< ']
    microservice_legend = ['L', 'Lr2']
    multi_legend = ['L', 'L', 'Lr2', 'Lr2']
    lv_ls_legend = ['Lr2 base', 'L base', ' L ', '  L ', ' Lr2', '  Lr2', 'L v s', 'Lr2 v s']

    print(f'\nBaseline GFlops: {baseline_gflops}')
    filename = 'baseline.csv'
    create_csv(filename, baseline_legend, baseline_gflops)
    barplot(filename, x_label='Baseline Tests', y_label='Average GFlops per 500 Trials', img_title='baseline_tests')

    print(f'\nReduced Linpack GFlops: {reduced_gflops}')
    filename = 'reduced.csv'
    create_csv(filename, reduced_legend, reduced_gflops)
    barplot(filename, x_label='Reduced Linpack Tests', y_label='Average GFlops per 500 Trials', img_title='reduced_tests')

    print(f'Microservice GFlops: {microservice_gflops}')
    filename = 'microservice.csv'
    create_csv(filename, microservice_legend, microservice_gflops)
    barplot(filename, x_label='Microservice Tests', y_label='Average GFlops per 500 Trials', img_title='microservice_tests')

    print(f'Multi-core GFlops: {multi_gflops}')
    filename = 'multi.csv'
    create_csv(filename, multi_legend, multi_gflops)
    barplot(filename, x_label='Multi-Core Container Tests', y_label='Average GFlops per 500 Trials', img_title='multi_tests')

    print(f'Linpack Versus GFlops: {lv_ls_gflops}')
    filename = 'lv_ls.csv'
    create_csv(filename, lv_ls_legend, lv_ls_gflops)
    barplot(filename, x_label='Linpack Versus Tests', y_label='Average GFlops per 500 Trials', img_title='lv_ls_tests')


def parse_file(logfile: str) -> float:
    """
    Grab the GFlops data from the log and store in data structure for graphing
    :param logfile: the logfile containing the benchmark results
    :return: return the gflop measuremnts
    """
    start = -1  # Line starting measurement table values
    average = 0.0

    # Reduce the logfile data to the benchmark measurements
    with open('./graph_data/' + logfile, 'r') as f:
        for count, line in enumerate(f):
            if 'Performance' in line:
                start = count + 3
            elif count == start:
                average = line.split()[3]
                break
        f.close()

    return average


if __name__ == '__main__':
    print('\nparsing results...')
    parse_tests()
    print('\nDone!')
