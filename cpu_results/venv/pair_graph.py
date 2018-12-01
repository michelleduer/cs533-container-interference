#!/usr/bin/env python3

import matplotlib.pyplot as plt     # visual plotting of data
import seaborn as sns               # visual plotting of data
import pandas as pd     # handling data


def paired_barplot(filename: str, x_label: str, y_label: str, img_title: str, pairs: [str]):
    """
    Graph barplot from resulting benchmarking measuremnt(s)
    :param filename: file containing data
    :param x_label: x label's name
    :param y_label: y label's name
    :param img_title: title of saved file
    """
    sns.set(style='whitegrid')
    df = pd.read_csv('./csv/' + filename)
    sns.set_palette(sns.color_palette(pairs))
    ax = sns.catplot(x='Linpack',
                     y='Gflops',
                     hue='Tests',
                     kind='bar',
                     data=df,
                     legend=False)

    ax.set(xlabel=x_label, ylabel=y_label)

    # Save plot image
    img = './graph/' + img_title
    plt.savefig(img)

    # Display plot
    plt.show()


if __name__ == '__main__':
    pairs = ['#256BCE', '#2FB9D0']
    paired_barplot('lv_ls.csv', 'Linpack Versus Tests', 'Average GFlops per 500 Trials', 'linpack_versus.png', pairs)
    reduced_pairs = ['#35D564', '#C491EC']
    paired_barplot('reduced.csv', 'Reduced Linpack Tests', 'Average GFlops per 500 Trials', 'reduced_linpack.png',
                   reduced_pairs)
    print('\nDone!')
