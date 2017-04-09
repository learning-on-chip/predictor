import datetime
import inspect
import logging
import numpy as np
import os

def ask(*options):
    print('Choose one of the following options:')
    for i, option in enumerate(options):
        print('    {}. {}'.format(i, option))
    while True:
        try:
            i = int(input('Your choice: '))
        except ValueError:
            continue
        if i < 0 or i >= len(options):
            continue
        return i

def default_output():
    return os.path.join('output', format_timestamp())

def figure(width=14, height=6):
    import matplotlib.pyplot as pp
    pp.figure(figsize=(width, height), dpi=80, facecolor='w', edgecolor='k')

def format_timestamp():
    return '{:%Y-%m-%d %H-%M-%S}'.format(datetime.datetime.now())

def format_percentage(count, total):
    return '{} ({:.2f}%)'.format(count, 100 * count / total)

def log(*arguments, name_limit=8, number_limit=4):
    arguments = list(arguments)
    first = arguments.pop(0)
    if isinstance(first, str):
        message = first
        name = 'Main'
        number = 0
    elif inspect.isclass(first):
        message = arguments.pop(0)
        name = first.__name__
        number = 0
    else:
        message = arguments.pop(0)
        name = first.__class__.__name__
        number = id(first)
    name = ('{:' + str(name_limit) + '}').format(name)
    name = name[:name_limit].upper()
    number = ('{:0' + str(number_limit) + '}').format(number)
    number = number[-number_limit:]
    logging.info('[%s|%s] %s', name, number, message.format(*arguments))

def loggalize(level=logging.INFO):
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=level)

def shift(data, amount, padding=0.0):
    data = np.roll(data, amount, axis=0)
    if amount > 0:
        data[:amount, :] = padding
    elif amount < 0:
        data[amount:, :] = padding
    return data

def tokenize(dictionary):
    chunks = []
    for key in sorted(dictionary.keys()):
        alias = ''.join([chunk[0] for chunk in key.split('_')])
        value = str(dictionary[key]).replace(' ', '')
        chunks.append('{}={}'.format(alias, value))
    return ','.join(chunks).lower()
