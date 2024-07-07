import itertools
import os
import plistlib
import unicodedata
import sys

from xml.etree.ElementTree import Element, SubElement, tostring

UNESCAPE_CHARACTERS = " ;()"

_MAX_RESULTS_DEFAULT = 9

# Updated to use plistlib.load for Python 3 compatibility
with open('info.plist', 'rb') as fp:
    preferences = plistlib.load(fp)
bundleid = preferences['bundleid']

class Item:
    @classmethod
    def unicode(cls, value):
        try:
            items = iter(value.items())
        except AttributeError:
            # Directly return the value if it's not a dict
            return str(value)
        else:
            # Use str instead of unicode for Python 3 compatibility
            return dict(map(cls.unicode, item) for item in items)

    def __init__(self, attributes, title, subtitle, icon=None):
        self.attributes = attributes
        self.title = title
        self.subtitle = subtitle
        self.icon = icon

    def __str__(self):
        return tostring(self.xml()).decode('utf-8')

    def xml(self):
        item = Element('item', self.unicode(self.attributes))
        for attribute in ('title', 'subtitle', 'icon'):
            value = getattr(self, attribute)
            if value is None:
                continue
            if len(value) == 2 and isinstance(value[1], dict):
                (value, attributes) = value
            else:
                attributes = {}
            SubElement(item, attribute, self.unicode(attributes)).text = self.unicode(value)
        return item

def args(characters=None):
    return tuple(unescape(decode(arg), characters) for arg in sys.argv[1:])

def config():
    return _create('config')

def decode(s):
    # Removed .decode('utf-8') as strings are already Unicode in Python 3
    return unicodedata.normalize('NFD', s)

def env(key):
    return os.environ[f'alfred_{key}']

def uid(uid):
    return '-'.join(map(str, (bundleid, uid)))

def unescape(query, characters=None):
    for character in (UNESCAPE_CHARACTERS if (characters is None) else characters):
        query = query.replace(f'\\{character}', character)
    return query

def work(volatile):
    path = {
        True: env('workflow_cache'),
        False: env('workflow_data')
    }[bool(volatile)]
    return _create(path)

def write(text):
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    sys.stdout.write(text)

def xml(items, maxresults=_MAX_RESULTS_DEFAULT):
    root = Element('items')
    for item in itertools.islice(items, maxresults):
        root.append(item.xml())
    return tostring(root, encoding='utf-8')

def _create(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.access(path, os.W_OK):
        raise IOError(f'No write access: {path}')
    return path
