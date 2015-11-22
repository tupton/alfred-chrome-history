from __future__ import print_function

import alfred
import sqlite3
import shutil
import os
import sys
from time import time

HISTORY_CACHE_TIME = 60
LOCAL_HISTORY_DB = 'History'

class ErrorItem(alfred.Item):
    def __init__(self, error):
        alfred.Item.__init__(self, {}, error.message, 'Check the workfrow log for more information.')

def alfred_error(error):
    alfred.write(alfred.xml([error]))

def copy_history(profile):
    history_file = os.path.join(os.path.expanduser(profile), 'History')

    if os.path.isfile(LOCAL_HISTORY_DB) and os.path.getmtime(LOCAL_HISTORY_DB) > time() - HISTORY_CACHE_TIME:
        return

    if os.path.isfile(history_file):
        shutil.copy(history_file, LOCAL_HISTORY_DB)

    if not os.path.isfile(LOCAL_HISTORY_DB):
        raise IOError('Unable to copy Google Chrome history database from {}'.format(history_file))

def get_history(query):
    conn = sqlite3.connect('History')
    c = conn.cursor()
    q = u'%{}%'.format(query)
    rows = c.execute(u'SELECT id,title,url FROM urls WHERE (title LIKE ? OR url LIKE ?) ORDER BY last_visit_time DESC', (q, q,))
    return rows

if __name__ == '__main__':
    (profile, query) = alfred.args()

    try:
        copy_history(profile)
    except IOError, e:
        alfred_error(ErrorItem(e))
        sys.exit(-1)

    rows = get_history(query)
    items = [alfred.Item({u'uid': alfred.uid(uid), u'arg': url}, title, url) for (uid, title, url) in rows]
    xml = alfred.xml(items)
    alfred.write(xml)
