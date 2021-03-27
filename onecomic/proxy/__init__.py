import os
import re
import importlib
HERE = os.path.abspath(os.path.dirname(__file__))


class ProxyBase(object):
    PROXY = None

    @classmethod
    def get_proxy(cls):
        return cls.PROXY

    @classmethod
    def init(cls, proxy, **kwargs):
        cls.PROXY = proxy

    @classmethod
    def test_proxy(cls):
        return True


def find_all_proxy_cls():
    for file in os.listdir(HERE):
        if re.match(r"^[a-zA-Z].*?\.py$", file):
            importlib.import_module(".{}".format(file.split(".")[0]), __package__)
    all_proxy_cls = {}
    for proxy_cls in ProxyBase.__subclasses__():
        all_proxy_cls[proxy_cls.NAME] = proxy_cls
    return all_proxy_cls


ALL_PROXY_CLS = find_all_proxy_cls()


def get_proxy_cls(name):
    return ALL_PROXY_CLS.get(name, ProxyBase)
