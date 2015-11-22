from __future__ import print_function

import alfred
import sqlite3
import shutil
import os

def copy_history(profile):
    history_file = os.path.join(profile, 'History')

    if os.path.isfile('History'):
        return

    if os.path.isfile(history_file):
        shutil.copy(history_file, 'History')

def get_history(query):
    conn = sqlite3.connect('History')
    c = conn.cursor()
    q = '%{}%'.format(query)
    rows = c.execute('SELECT title,url FROM urls WHERE (title LIKE ? OR url LIKE ?) ORDER BY last_visit_time DESC', (q, q,))
    return rows

if __name__ == '__main__':
    (profile, query) = alfred.args()

    copy_history(profile)
    rows = get_history(query)
    items = [alfred.Item({'uid': row[1], 'arg': row[1]}, row[0], row[1]) for row in rows]
    xml = alfred.xml(items)
    alfred.write(xml)
