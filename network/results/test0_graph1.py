#!/usr/bin/python3
import seaborn
import pandas

# File to operate on.
plot = 'test0_graph1'

# Set Seaborn defaults.
seaborn.set()

# Read data set.
data = pandas.read_csv(plot + '.csv')

# Create base graph.
graph = seaborn.catplot(x='Server',
                        y='Throughput',
                        hue='Client',
                        kind='bar',
                        data=data)

# Set axis labels.
graph.set(xlabel='Server configuration',
          ylabel='Throughput (Gbps)',
          title='iperf3 Throughput (Local Server)')

# Set value labels.
# for index, row in data.iterrows():
#     graph.ax.text(row.x, row.Throughput, row.Throughput)
# for p in graph.ax.patches:
#     graph.ax.text(p.get_x() + p.get_width() / 2,
#                   p.get_height(),
#                   "%.1f" % p.get_height(),
#                   ha='center',
#                   va='bottom')

# Save graph.
graph.savefig(plot + '.png')

