#!/usr/bin/env python3

import math
import matplotlib.pyplot as plt
import numpy as np
import sqlite3

def read(path='tests/fixtures/google.sqlite3'):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT time FROM arrivals ORDER BY time')
    data = np.diff(np.array([row[0] for row in cursor]))
    connection.close()
    return data

data = read()
mean, variance = np.mean(data), np.var(data)

print('Samples: %d' % len(data))
print('Mean: %.4f ± %.4f' % (mean, math.sqrt(variance)))
print('Minimum: %e' % np.min(data))
print('Maximum: %e' % np.max(data))

plt.figure(num=None, figsize=(12, 8), dpi=80, facecolor='w', edgecolor='k')
plt.hist(np.log10(data), bins=1000, log=True)
plt.title('Histogram of interarrivals')
plt.xlabel('log(time)')
plt.ylabel('log(count)')
plt.show()
