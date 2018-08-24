#!/usr/bin/env python

"""
Get relevant history from the Google Chrome history database based on the given query and build
Alfred items based on the results.

Usage:
    chrome.py [--no-favicons | --favicons] PROFILE QUERY
    chrome.py (-h | --help)
    chrome.py --version

The path to the Chrome user profile to get the history database from is given in PROFILE. The query
to search for is given in QUERY. The output is formatted as the Alfred script filter XML output
format.

    PROFILE  The path to the Chrome profile whose history database should be searched
    QUERY    The query to search the history database with

Options:
    --no-favicons  Do not return Alfred XML results with favicons [default: false]
    --favicons     Include favicons in the Alfred XML results [default: true]
"""

from __future__ import print_function

import alfred
import sqlite3
import shutil
import os
import sys
import time
import datetime
from docopt import docopt

__version__ = '0.7.0'

CACHE_EXPIRY = 60
HISTORY_DB = 'History'
FAVICONS_DB = 'Favicons'
FAVICONS_CACHE = 'Favicons-Cache'

FAVICON_JOIN = u"""
    LEFT OUTER JOIN icon_mapping ON icon_mapping.page_url = urls.url,
                    favicon_bitmaps ON favicon_bitmaps.id =
                        (SELECT id FROM favicon_bitmaps
                            WHERE favicon_bitmaps.icon_id = icon_mapping.icon_id
                            ORDER BY width DESC LIMIT 1)
"""
FAVICON_SELECT = u"""
    , favicon_bitmaps.image_data, favicon_bitmaps.last_updated
"""

HISTORY_QUERY = u"""
SELECT urls.id, urls.title, urls.url {favicon_select}
    FROM urls
    {favicon_join}
    WHERE (urls.title LIKE ? OR urls.url LIKE ?)
    ORDER BY visit_count DESC, typed_count DESC, last_visit_time DESC
"""

UNIX_EPOCH = datetime.datetime.utcfromtimestamp(0)
WINDOWS_EPOCH = datetime.datetime(1601, 1, 1)
SECONDS_BETWEEN_UNIX_AND_WINDOWS_EPOCH = (UNIX_EPOCH - WINDOWS_EPOCH).total_seconds()
MICROSECS_PER_SEC = 10 ** -6

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

def history_db(profile, favicons=True):
    history = copy_db(HISTORY_DB, profile)
    db = sqlite3.connect(history)
    if favicons:
        favicons = copy_db(FAVICONS_DB, profile)
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

def history_results(db, query, favicons=True):
    q = u'%{}%'.format(query)
    if favicons:
        favicon_select = FAVICON_SELECT
        favicon_join = FAVICON_JOIN
    else:
        favicon_select = ''
        favicon_join = ''
    for row in db.execute(HISTORY_QUERY.format(favicon_select=favicon_select, favicon_join=favicon_join), (q, q,)):
        if favicons:
            (uid, title, url, image_data, image_last_updated) = row
            icon = cache_favicon(image_data, uid, convert_chrometime(image_last_updated)) if image_data and image_last_updated else None
        else:
            (uid, title, url) = row
            icon = None

        yield alfred.Item({u'uid': alfred.uid(uid), u'arg': url, u'autocomplete': url}, title or url, url, icon)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Alfred Chrome History {}'.format(__version__))
    favicons = arguments.get('--no-favicons') is False

    profile = unicode(arguments.get('PROFILE'), encoding='utf-8', errors='ignore')
    query = unicode(arguments.get('QUERY'), encoding='utf-8', errors='ignore')

    try:
        db = history_db(profile, favicons=favicons)
    except IOError, e:
        alfred_error(e)
        sys.exit(-1)

    alfred.write(alfred.xml(history_results(db, query, favicons=favicons)))
