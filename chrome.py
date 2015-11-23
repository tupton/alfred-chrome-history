from __future__ import print_function

import alfred
import sqlite3
import shutil
import os
import sys
import time

HISTORY_CACHE_EXPIRY = 60
HISTORY_DB = 'History'
HISTORY_CACHE = os.path.join(alfred.work(True), HISTORY_DB)
HISTORY_QUERY = u"""
SELECT id,title,url FROM urls WHERE (title LIKE ? OR url LIKE ?) ORDER BY last_visit_time DESC
"""

class ErrorItem(alfred.Item):
    def __init__(self, error):
        alfred.Item.__init__(self, {u'valid': u'NO'}, error.message, u'Check the workflow log for more information.')

def alfred_error(error):
    alfred.write(alfred.xml([ErrorItem(error)]))

def copy_history(profile):
    if os.path.isfile(HISTORY_CACHE) and time.time() - os.path.getmtime(HISTORY_CACHE) < HISTORY_CACHE_EXPIRY:
        return HISTORY_CACHE

    history_file = os.path.join(os.path.expanduser(profile), HISTORY_DB)
    try:
        shutil.copy(history_file, HISTORY_CACHE)
    except:
        raise IOError(u'Unable to copy Google Chrome history database from {}'.format(history_file))

    return HISTORY_CACHE

def history_db(profile):
    history = copy_history(profile)
    db = sqlite3.connect(history)
    return db

def history_results(db, query):
    q = u'%{}%'.format(query)
    for row in db.execute(HISTORY_QUERY, (q, q,)):
        (uid, title, url) = row
        yield alfred.Item({u'uid': alfred.uid(uid), u'arg': url}, title or url, url)

if __name__ == '__main__':
    (profile, query) = alfred.args()

    try:
        db = history_db(profile)
    except IOError, e:
        alfred_error(e)
        sys.exit(-1)

    alfred.write(alfred.xml(history_results(db, query)))
