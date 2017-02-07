#!/usr/bin/env python3

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

import glob, json
import numpy as np

import task_usage

def main(data_path, index_path):
    count = 0
    index = []
    for path in sorted(glob.glob('{}/**/*.sqlite3'.format(data_path))):
        data = task_usage.count_job_task_samples(path)
        for i in range(data.shape[0]):
            index.append({
                'path': path,
                'job': int(data[i, 0]),
                'task': int(data[i, 1]),
                'count': int(data[i, 2]),
            })
        count += 1
        if count % 10000 == 0:
            print('Processed: {}'.format(count))
    with open(index_path, 'w') as file:
        json.dump({'index': index}, file, indent=4)

if __name__ == '__main__':
    assert(len(sys.argv) == 3)
    main(sys.argv[1], sys.argv[2])
