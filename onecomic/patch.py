import subprocess
import platform

SYSTEM = platform.system()

class Popen(subprocess.Popen):

    def __init__(self, *args, **kwargs):
        if SYSTEM == 'Windows':
            kwargs['encoding'] = kwargs.get('encoding') or 'utf-8'
        super().__init__(*args, **kwargs)


def patch_all():
    subprocess.Popen = Popen
