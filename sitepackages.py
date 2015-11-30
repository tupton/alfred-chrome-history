from __future__ import print_function

import sys
import site

if hasattr(sys, 'real_prefix'):
    site_packages = [p for p in sys.path if p.endswith('site-packages')]
    if len(site_packages) > 0:
        print('{}'.format(site_packages[-1]))
else:
    print(site.getsitepackages()[0])
