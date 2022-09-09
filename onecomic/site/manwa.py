"""
解密方法参考
https://github.com/coofo/someScript/blob/main/tampermonkey/manwa.user.js

将 eval 改成 console.log 既可以看到源码
https://manwa.site/static/js/ch.js?v=202208132
"""
import re
import logging
from urllib.parse import urljoin
from Cryptodome.Cipher import AES

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


KEY = b"my2ecret782ecret"
IV = KEY


def add_to_16(value):
    while len(value) % 16 != 0:
        value += b'\x10'
    return value


def aes_encrypt(key, t, iv):
    aes = AES.new(add_to_16(key), AES.MODE_CBC, add_to_16(iv))
    return aes.encrypt(add_to_16(t))


def aes_decrypt(key, t, iv):
    aes = AES.new(add_to_16(key), AES.MODE_CBC, add_to_16(iv))
    return aes.decrypt(t).rstrip(b'\x10')


def image_pipeline(image_path):
    data = open(image_path, 'rb').read()
    new_data = aes_decrypt(KEY, data, IV)
    with open(image_path, 'wb') as f:
        f.write(new_data)


class BaozimhCrawler(CrawlerBase):

    SITE = "manwa"
    SITE_INDEX = 'https://manwa.site/'
    SOURCE_NAME = "漫蛙漫画"
    LOGIN_URL = SITE_INDEX

    COMICID_PATTERN = re.compile(r'/book/(\d+)/?')
    DEFAULT_COMICID = '22270'
    DEFAULT_SEARCH_NAME = ''
    DEFAULT_TAG = ""

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, '/book/%s' % comicid)

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.find('p', {'class': 'detail-main-info-title'}).text.strip()
        author = ','.join([
            i.text.strip() for i in soup.find('span', {'class': 'detail-main-info-value'}).find_all('a')
        ])
        desc = soup.find('p', {'class': 'detail-desc'}).text.strip()
        cover_image_url = soup.find('div', {'class': 'detail-main-cover'}).img.get("data-original")
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)
        for idx, li in enumerate(soup.find('ul', {"id": "detail-list-select"}).find_all('li'), start=1):
            href = li.a.get('href')
            source_url = urljoin(self.SITE_INDEX, href)
            title = li.a.get('title') or li.a.text.strip()
            book.add_chapter(chapter_number=idx,
                             source_url=source_url,
                             title=title)
        return book

    def get_chapter_item(self, citem):
        soup = self.get_soup(citem.source_url)
        image_urls = [img.get('data-r-src') for img in soup.find_all('img') if img.get('data-r-src')]
        citem.image_pipelines = [image_pipeline for i in image_urls]
        citem.image_urls = image_urls
        return citem

    def latest(self, page=1):
        url = urljoin(self.SITE_INDEX, "/getUpdate") + "?page=%s&date=" % (page - 1) * 15

        data = self.get_json(url)
        result = self.new_search_result_item()
        for i in data['books']:
            comicid = i['id']
            source_url = self.get_source_url(comicid)
            name = i['book_name']
            cover_image_url = i['cover_url']
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def search(self, name, page, size=None):
        if page > 1:
            return self.new_search_result_item()
        result = self.new_search_result_item()
        url = urljoin(self.SITE_INDEX, "/search") + "?keyword=%s" % name
        soup = self.get_soup(url)
        for li in soup.find('ul', {'class': 'book-list'}).find_all('li'):
            href = li.a.get('href')
            title = li.a.get('title')
            comicid = self.get_comicid_by_url(href)
            source_url = self.get_source_url(comicid)
            cover_image_url = li.a.img.get('data-original') or li.a.img.get('src')
            result.add_result(comicid=comicid,
                              name=title,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result
