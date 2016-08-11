import matplotlib.pyplot as pp
import numpy as np
import sqlite3

DATABASE_PATH = 'tests/fixtures/google.sqlite3'

def count_apps(path=DATABASE_PATH):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(DISTINCT app) FROM jobs')
    data = cursor.fetchone()[0]
    connection.close()
    return data

def count_users(path=DATABASE_PATH):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(DISTINCT user) FROM jobs')
    data = cursor.fetchone()[0]
    connection.close()
    return data

def count_user_jobs(path=DATABASE_PATH):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('SELECT user, COUNT(time) FROM jobs GROUP BY user')
    data = np.array([row for row in cursor])
    connection.close()
    return data

def diff(data):
    data = np.vstack((np.diff(data[:, 0]), data[1:, 1], data[1:, 2]))
    return np.transpose(data)

def figure(width=14, height=6):
    pp.figure(figsize=(width, height), dpi=80, facecolor='w', edgecolor='k')

def normalize(data):
    return (data - np.mean(data)) / np.sqrt(np.var(data))

def select_data(app=None, user=None, path=DATABASE_PATH):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    sql = 'SELECT time, app, user FROM jobs'
    if app is not None or user is not None: sql += ' WHERE'
    if app is not None:
        app = app if hasattr(app, '__iter__') else [app]
        sql += ' app in ({})'.format(', '.join([str(app) for app in app]))
    if app is not None and user is not None: sql += ' AND'
    if user is not None:
        user = user if hasattr(user, '__iter__') else [user]
        sql += ' user in ({})'.format(', '.join([str(user) for user in user]))
    sql += ' ORDER BY time'
    cursor.execute(sql)
    data = np.array([row for row in cursor])
    connection.close()
    return data
