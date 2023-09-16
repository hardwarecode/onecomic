import subprocess
import platform
import collections
import sys

SYSTEM = platform.system()


class Popen(subprocess.Popen):

    def __init__(self, *args, **kwargs):
        if SYSTEM == 'Windows':
            kwargs['encoding'] = kwargs.get('encoding') or 'utf-8'
        super().__init__(*args, **kwargs)


def patch_abc():
    if sys.version_info.major == 3 and sys.version_info.minor >= 10:
        collections.MutableSet = collections.abc.MutableSet
        collections.MutableMapping = collections.abc.MutableMapping


def patch_all():
    subprocess.Popen = Popen
    patch_abc()
