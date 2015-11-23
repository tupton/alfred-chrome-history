from __future__ import print_function

import alfred
import sqlite3
import shutil
import os
import sys
from time import time

HISTORY_CACHE_EXPIRY = 60
LOCAL_HISTORY_DB = 'History'

class ErrorItem(alfred.Item):
    def __init__(self, error):
        alfred.Item.__init__(self, {}, error.message, 'Check the workfrow log for more information.')

def alfred_error(error):
    alfred.write(alfred.xml([error]))

def copy_history(profile):
    history_file = os.path.join(os.path.expanduser(profile), 'History')
    history = LOCAL_HISTORY_DB

    if os.path.isfile(LOCAL_HISTORY_DB) and time() - os.path.getmtime(LOCAL_HISTORY_DB) < HISTORY_CACHE_EXPIRY:
        return history

    if os.path.isfile(history_file):
        shutil.copy(history_file, LOCAL_HISTORY_DB)

    if not os.path.isfile(LOCAL_HISTORY_DB):
        raise IOError('Unable to copy Google Chrome history database from {}'.format(history_file))

    return history

def history_db(profile):
    history = copy_history(profile)
    db = sqlite3.connect(history)
    return db

def history_results(db, query):
    q = u'%{}%'.format(query)
    for row in db.execute(u'SELECT id,title,url FROM urls WHERE (title LIKE ? OR url LIKE ?) ORDER BY last_visit_time DESC', (q, q,)):
        (uid, title, url) = row
        yield alfred.Item({u'uid': alfred.uid(uid), u'arg': url}, title, url)

if __name__ == '__main__':
    (profile, query) = alfred.args()

    try:
        db = history_db(profile)
    except IOError, e:
        alfred_error(ErrorItem(e))
        sys.exit(-1)

    alfred.write(alfred.xml(history_results(db, query)))
