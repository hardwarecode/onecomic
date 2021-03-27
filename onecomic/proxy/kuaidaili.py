import requests
from . import ProxyBase


class KuaidailiProxy(ProxyBase):
    NAME = 'kuaidaili'
    API_URL = None
    session = requests.Session()

    @classmethod
    def get_proxy(cls):
        assert cls.API_URL, 'KuaidailiProxy API_URL not set'
        proxy_ip = cls.session.get(cls.API_URL).text
        return "socks5://%(proxy)s/" % {"proxy": proxy_ip}

    @classmethod
    def init(cls, api_url, **kwargs):
        cls.API_URL = api_url
