import os
import configparser
import logging

from copy import deepcopy

logger = logging.getLogger(__name__)


class CrawlerConfig(object):
    DOWNLOAD_DIR = 'download_dir'
    CONFIG_FILE = 'config'
    DRIVER_TYPE = 'driver_type'
    DRIVER_PATH = 'driver_path'
    COOKIES_PATH = 'cookies_path'
    COOKIES_DIR = 'cookies_dir'
    QUALITY = 'quality'
    MAX_HEIGHT = 'max_height'
    NODE_MODULES = 'node_modules'
    WORKER = 'worker'
    IMAGE_TIMEOUT = 'image_timeout'
    CRAWLER_TIMEOUT = 'crawler_timeout'
    CRAWLER_DELAY = 'crawler_delay'

    DEFAULT_VALUE = {
        DOWNLOAD_DIR: 'download',
        DRIVER_TYPE: 'Chrome',
        QUALITY: 95,
        MAX_HEIGHT: 20000,
        NODE_MODULES: 'node_modules',
        CONFIG_FILE: 'config.ini',
        WORKER: 4,
        IMAGE_TIMEOUT: 30,
        CRAWLER_TIMEOUT: 30,
        CRAWLER_DELAY: 0,
    }

    TO_ENV_KEY = {
        DOWNLOAD_DIR: 'ONECOMIC_DOWNLOAD_DIR',
        CONFIG_FILE: 'ONECOMIC_CONFIG_FILE',
        DRIVER_TYPE: 'ONECOMIC_DRIVER_TYPE',
        DRIVER_PATH: 'ONECOMIC_DRIVER_PATH',
        COOKIES_DIR: 'ONECOMIC_COOKIES_DIR',
        QUALITY: 'ONECOMIC_QUALITY',
        MAX_HEIGHT: 'ONECOMIC_MAX_HEIGHT',
        NODE_MODULES: 'ONECOMIC_NODE_MODULES',
        WORKER: 'ONECOMIC_WORKER',
        IMAGE_TIMEOUT: 'ONECOMIC_IMAGE_TIMEOUT',
        CRAWLER_TIMEOUT: 'ONECOMIC_CRAWLER_TIMEOUT',
        CRAWLER_DELAY: 'ONECOMIC_CRAWLER_DELAY'
    }

    def __init__(self, args=None):
        self.args = args
        self.config = deepcopy(self.DEFAULT_VALUE)
        self.config.update(self.read_config(self.get_config_file()))

        for key in self.TO_ENV_KEY:
            value = os.environ.get(self.TO_ENV_KEY[key])
            if value:
                self.config[key] = value
        if args:
            for key in args.__dict__:
                value = getattr(args, key)
                if key == 'output':
                    key = self.DOWNLOAD_DIR

                if value is not None:
                    self.config[key] = value
        logger.debug('CrawlerConfig config=%s', self.config)

    def get_config_file(self):
        config_file = None
        if self.args:
            config_file = self.args.config
        if not config_file:
            config_file = os.environ.get(self.TO_ENV_KEY[self.CONFIG_FILE])
        if not config_file:
            config_file = self.config[self.CONFIG_FILE]
        return config_file

    @classmethod
    def read_config(cls, filepath):
        config = {}
        if filepath and os.path.exists(filepath):
            logger.info(f'loading config. config={filepath}')
            section = 'crawler'
            parser = configparser.ConfigParser()
            parser.read(filepath, encoding='utf-8')
            if parser.has_section(section):
                config = {key: parser.get(section, key) for key in parser.options(section)}
        return config

    def get_proxy(self, site):
        if self.args and self.args.proxy:
            return self.args.proxy
        proxy = self.config.get(f'proxy_{site}', '')
        if not proxy:
            proxy = os.environ.get('ONECOMIC_PROXY_{}'.format(site.upper()))
        return proxy

    def get_cookies_path(self, site):
        cookies_path = None
        if site:
            cookies_path = self.config.get(self.COOKIES_PATH)
        if not cookies_path:
            cookies_dir = self.config.get(self.COOKIES_DIR, '')
            cookies_path = os.path.join(cookies_dir, f'{site}.json')
        return cookies_path

    @property
    def download_dir(self):
        return self.config[self.DOWNLOAD_DIR]

    @property
    def driver_type(self):
        return self.config.get(self.DRIVER_TYPE, '')

    @property
    def driver_path(self):
        return self.config.get(self.DRIVER_PATH, '')

    @property
    def quality(self):
        return int(self.config[self.QUALITY])

    @property
    def max_height(self):
        return int(self.config[self.MAX_HEIGHT])

    @property
    def node_modules(self):
        return self.config[self.NODE_MODULES]

    @property
    def output(self):
        return self.config[self.DOWNLOAD_DIR]

    @property
    def worker(self):
        return int(self.config[self.WORKER])

    @property
    def crawler_timeout(self):
        return int(self.config[self.CRAWLER_TIMEOUT])

    @property
    def image_timeout(self):
        return int(self.config[self.IMAGE_TIMEOUT])

    @property
    def crawler_delay(self):
        return int(self.config[self.CRAWLER_DELAY])
