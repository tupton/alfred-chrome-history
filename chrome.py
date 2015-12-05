from __future__ import print_function

import alfred
import sqlite3
import shutil
import os
import sys
import time
import datetime

CACHE_EXPIRY = 60
HISTORY_DB = 'History'
FAVICONS_DB = 'Favicons'
FAVICONS_CACHE = 'Favicons-Cache'
HISTORY_QUERY = u"""
SELECT urls.id, urls.title, urls.url, favicon_bitmaps.image_data, favicon_bitmaps.last_updated
    FROM urls
    LEFT OUTER JOIN icon_mapping ON icon_mapping.page_url = urls.url,
                    favicon_bitmaps ON favicon_bitmaps.id =
                        (SELECT id FROM favicon_bitmaps
                            WHERE favicon_bitmaps.icon_id = icon_mapping.icon_id
                            ORDER BY width DESC LIMIT 1)
    WHERE (urls.title LIKE ? OR urls.url LIKE ?)
    ORDER BY visit_count DESC, typed_count DESC, last_visit_time DESC
"""
UNIX_EPOCH = datetime.datetime.utcfromtimestamp(0)
WINDOWS_EPOCH = datetime.datetime(1601, 1, 1)
SECONDS_BETWEEN_UNIX_AND_WINDOWS_EPOCH = (UNIX_EPOCH - WINDOWS_EPOCH).total_seconds()
MICROSECS_PER_SEC = 10**-6


class ErrorItem(alfred.Item):
    def __init__(self, error):
        alfred.Item.__init__(self, {u'valid': u'NO', u'autocomplete': error.message}, error.message, u'Check the workflow log for more information.')

def alfred_error(error):
    alfred.write(alfred.xml([ErrorItem(error)]))

def copy_db(name, profile):
    cache = os.path.join(alfred.work(True), name)
    if os.path.isfile(cache) and time.time() - os.path.getmtime(cache) < CACHE_EXPIRY:
        return cache

    db_file = os.path.join(os.path.expanduser(profile), name)
    try:
        shutil.copy(db_file, cache)
    except:
        raise IOError(u'Unable to copy Google Chrome history database from {}'.format(db_file))

    return cache


def history_db(profile):
    history = copy_db(HISTORY_DB, profile)
    favicons = copy_db(FAVICONS_DB, profile)
    db = sqlite3.connect(history)
    db.cursor().execute('ATTACH DATABASE ? AS favicons', (favicons,)).close()
    return db


def cache_favicon(image_data, uid, last_updated):
    cache_dir = os.path.join(alfred.work(True), FAVICONS_CACHE)
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)
    icon_file = os.path.join(cache_dir, str(uid))
    if not os.path.isfile(icon_file) or last_updated > os.path.getmtime(icon_file):
        with open(icon_file, 'w') as f:
            f.write(image_data)
        os.utime(icon_file, (time.time(), last_updated))

    return (icon_file, {'type': 'png'})


# Chrome measures time in microseconds since the Windows epoch (1601/1/1)
# https://code.google.com/p/chromium/codesearch#chromium/src/base/time/time.h
def convert_chrometime(chrometime):
    return (chrometime * MICROSECS_PER_SEC) - SECONDS_BETWEEN_UNIX_AND_WINDOWS_EPOCH


def history_results(db, query):
    q = u'%{}%'.format(query)
    for row in db.execute(HISTORY_QUERY, (q, q,)):
        (uid, title, url, image_data, image_last_updated) = row
        icon = cache_favicon(image_data, uid, convert_chrometime(image_last_updated)) if image_data and image_last_updated else None
        yield alfred.Item({u'uid': alfred.uid(uid), u'arg': url, u'autocomplete': url}, title or url, url, icon)

if __name__ == '__main__':
    (profile, query) = alfred.args()

    try:
        db = history_db(profile)
    except IOError, e:
        alfred_error(e)
        sys.exit(-1)

    alfred.write(alfred.xml(history_results(db, query)))
