import httpx
from . import ProxyBase

SESSION = None


def get_session():
    global SESSION
    if SESSION is None:
        SESSION = httpx.Client(verify=False)
    return SESSION


class KuaidailiProxy(ProxyBase):
    NAME = 'kuaidaili'
    API_URL = None

    @classmethod
    def get_proxy(cls):
        assert cls.API_URL, 'KuaidailiProxy API_URL not set'
        session = get_session()
        proxy_ip = session.get(cls.API_URL).text
        return "socks5://%(proxy)s/" % {"proxy": proxy_ip}

    @classmethod
    def init(cls, api_url, **kwargs):
        cls.API_URL = api_url
