#!/usr/bin/python3
import seaborn
import pandas
import matplotlib.pyplot as plt

# File to operate on.
plot = 'test345_graph1'

# Set Seaborn defaults.
seaborn.set()

# Read data set.
data = pandas.read_csv(plot + '.csv')

# Create base graph.
graph = seaborn.catplot(x='Test configuration',
                        y='Throughput (Mbps)',
                        hue='Download type',
                        kind='bar',
                        data=data)

# Set axis labels.
graph.set(title='NGINX Throughput\n')
graph.ax.set_yticks(range(0,901,100))
plt.ylim(0,950)

# Set value labels.
#for index, row in data.iterrows():
#     graph.ax.text(row.name, row.Median, row.Median)

# Save graph.
graph.savefig(plot + '.png')

