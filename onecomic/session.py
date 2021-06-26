import json
import logging

import httpx
from httpx_socks import SyncProxyTransport

from .utils import ensure_file_dir_exists
from .proxy import get_proxy_cls, ALL_PROXY_CLS

logger = logging.getLogger(__name__)


class SessionMgr(object):
    SESSION_INSTANCE = {}
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36'
    }
    COOKIES_KEYS = ['name', 'value', 'path', 'domain']
    TIMEOUT_CONFIG = {}
    PROXY_CLS_CONFIG = {}
    HTTP_20_SITE = ['webtoons', 'toomics']

    @classmethod
    def get_timeout(cls, site, default=30):
        return cls.TIMEOUT_CONFIG.get(site, default)

    @classmethod
    def set_timeout(cls, site, timeout):
        cls.TIMEOUT_CONFIG[site] = timeout

    @classmethod
    def get_session(cls, site):
        if site not in cls.SESSION_INSTANCE:
            session = cls.new_session(site=site)
            cls.SESSION_INSTANCE[site] = session
        return cls.SESSION_INSTANCE[site]

    @classmethod
    def new_session(cls, site):
        http2 = site in cls.HTTP_20_SITE
        transport = None
        proxy_url = cls.get_proxy(site)
        if proxy_url:
            transport = SyncProxyTransport.from_url(proxy_url)
        session = httpx.Client(verify=False, http2=http2, transport=transport)
        session.headers.update(cls.DEFAULT_HEADERS)
        return session

    @classmethod
    def set_session(cls, site, session):
        cls.SESSION_INSTANCE[site] = session
        return session

    @classmethod
    def update_cookies(cls, site, cookies):
        session = cls.get_session(site=site)
        for cookie in cookies:
            data = {key: cookie.get(key) for key in cls.COOKIES_KEYS}
            session.cookies.set(**data)

    @classmethod
    def load_cookies(cls, site, path):
        with open(path) as f:
            cookies = json.load(f)
            cls.update_cookies(site=site, cookies=cookies)
        return cls.get_session(site=site)

    @classmethod
    def export_cookies(cls, site, path):
        cookies = cls.get_cookies(site)
        ensure_file_dir_exists(path)
        with open(path, 'w') as f:
            json.dump(cookies, f, indent=4)

    @classmethod
    def get_cookies(cls, site):
        cookies = []
        session = cls.get_session(site=site)
        for c in session.cookies:
            args = dict(vars(c).items())
            data = {key: args.get(key) for key in cls.COOKIES_KEYS}
            cookies.append(data)
        return cookies

    @classmethod
    def clear_cookies(cls, site):
        session = cls.get_session(site=site)
        session.cookies.clear()

    @classmethod
    def set_proxy(cls, site, proxy, **kwargs):
        proxy_cls = get_proxy_cls(proxy)
        if proxy in ALL_PROXY_CLS:
            proxy_cls.init(**kwargs)
        else:
            proxy_cls.init(proxy=proxy)
        cls.PROXY_CLS_CONFIG[site] = proxy_cls

        old_session = cls.get_session(site)
        new_session = cls.new_session(site)
        cls.set_session(site=site, session=new_session)
        old_session.close()

    @classmethod
    def get_proxy(cls, site):
        proxy_cls = cls.PROXY_CLS_CONFIG.get(site)
        if proxy_cls:
            return proxy_cls.get_proxy()
        return None


class CrawlerSession(SessionMgr):
    pass


class ImageSession(SessionMgr):
    pass
