#!/usr/bin/python3
import seaborn
import pandas

# File to operate on.
plot = 'test2_graph1'

# Set Seaborn defaults.
seaborn.set()

# Read data set.
data = pandas.read_csv(plot + '.csv')

# Create base graph.
graph = seaborn.catplot(x='Benchmark instance',
                        y='Throughput (Mbps)',
                        kind='bar',
                        data=data)

# Set axis labels.
graph.set(title='iperf3 Throughput\n(multiple instances, capped at 116 Mbps)')

# Set value labels.
#for index, row in data.iterrows():
#     graph.ax.text(row.name, row.Median, row.Median)

# Save graph.
graph.savefig(plot + '.png')

