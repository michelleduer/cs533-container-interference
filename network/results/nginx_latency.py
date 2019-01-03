#!/usr/bin/python3
import seaborn
import pandas

# File to operate on.
plot = 'nginx_latency'

# Set Seaborn defaults.
seaborn.set()

# Read data set.
data = pandas.read_csv(plot + '.csv')

# Create base graph.
graph = seaborn.catplot(x='Environment',
                        y='Latency (ms)',
                        kind='bar',
                        data=data)

# Set axis labels.
graph.set(title='NGINX latency for small file downloads')

# Set value labels.
#for index, row in data.iterrows():
#     graph.ax.text(row.name, row.Median, row.Median)

# Save graph.
graph.savefig(plot + '.png')


