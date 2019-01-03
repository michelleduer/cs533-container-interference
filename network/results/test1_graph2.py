#!/usr/bin/python3
import seaborn
import pandas

# File to operate on.
plot = 'test1_graph2'

# Set Seaborn defaults.
seaborn.set()

# Read data set.
data = pandas.read_csv(plot + '.csv')

# Create base graph.
graph = seaborn.catplot(x='Number of benchmarks',
                        y='Throughput (Mbps)',
                        hue='Type',
                        kind='bar',
                        data=data)

# Set axis labels.
graph.set(title='iperf3 Min/Median/Max Throughput\n(multiple instances, oversubscribed)')

# Set value labels.
#for index, row in data.iterrows():
#     graph.ax.text(row.name, row.Median, row.Median)

# Save graph.
graph.savefig(plot + '.png')

