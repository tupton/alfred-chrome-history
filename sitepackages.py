from __future__ import print_function

import sys
import site

def is_virtual_env():
    return hasattr(sys, 'real_prefix')

def virtual_env_site_packages():
    site_packages = [p for p in sys.path if p.endswith('site-packages')]
    if len(site_packages) > 0:
        return '{}'.format(site_packages[-1])

def site_packages():
    return site.getsitepackages()[0]

def get_site_packages():
    if is_virtual_env():
        return virtual_env_site_packages()
    else:
        return site_packages()

if __name__ == '__main__':
    print('{}'.format(get_site_packages()))
