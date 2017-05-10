
# Copyright (C) 2014 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import json
import platform
from collections import defaultdict

from anaconda_go.lib import go
from anaconda_go.lib.plugin import typing

cachepath = {
    'linux': os.path.join('~', '.local', 'share', 'anaconda', 'cache'),
    'darwin': os.path.join('~', 'Library', 'Cache', 'anaconda'),
    'windows': os.path.join(os.getenv('APPDATA') or '~', 'Anaconda', 'Cache')
}

cache_directory = os.path.expanduser(
    cachepath.get(platform.system().lower())
)

PACKAGES_CACHE = defaultdict(lambda: [])


def append(package: typing.Dict) -> None:
    """Append the given package into the cache
    """

    global PACKAGES_CACHE

    if not package_in_cache(package):
        PACKAGES_CACHE[go.GOROOT].append(package)


def package_in_cache(package: typing.Dict) -> bool:
    """Look for the given package in the cache and return true if is there
    """

    for pkg in PACKAGES_CACHE[go.GOROOT]:
        if pkg['ImportPath'] == package['ImportPath']:
            return True

    return False


def lookup(node_name: str='') -> typing.Dict:
    """Lookup the given node_name in the cache and return it back
    """

    node = {}
    if node_name == '':
        node = PACKAGES_CACHE[go.GOROOT]
    else:
        for pkg in PACKAGES_CACHE[go.GOROOT]:
            guru = pkg.get('Guru')
            if guru is None:
                continue
            path = guru['package'].get('path')
            if path is not None and path == node_name:
                node = guru
                break
            for member in guru['package'].get('members', []):
                if member.get('name') == node_name:
                    node = member
                    break
                for method in member.get('methods', []):
                    if method['name'] == node_name:
                        node = method
                        break

    return node


def persist_package_cache() -> None:
    """Write the contents of the package cache for this GOROOT into the disk
    """

    gopath = go.GOPATH.replace(os.path.sep, '_')
    cachefile = os.path.join(cache_directory, gopath, 'packages.cache')
    if not os.path.exists(os.path.dirname(cachefile)):
        os.makedirs(os.path.dirname(cachefile))

    with open(cachefile, 'w') as fd:
        json.dump(PACKAGES_CACHE[go.GOROOT], fd)


def load_package_cache() -> typing.List:
    """Load a previously stores package cache file
    """

    global PACKAGES_CACHE
    gopath = go.GOPATH.replace(os.path.sep, '_')
    cachefile = os.path.join(cache_directory, gopath, 'packages.cache')
    try:
        with open(cachefile, 'r') as fd:
            PACKAGES_CACHE[go.GOROOT] = json.load(fd)
    except FileNotFoundError:
        pass
