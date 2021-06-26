import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class PicxxxxCrawler(CrawlerBase):

    SITE = "picxxxx"
    SITE_INDEX = 'http://picxxxx.top/'
    SOURCE_NAME = "Nsfwpicx"
    LOGIN_URL = SITE_INDEX
    R18 = True

    DEFAULT_COMICID = '2020-12-08-2750'
    DEFAULT_SEARCH_NAME = ''
    DEFAULT_TAG = ""
    COMICID_PATTERN = re.compile(r'picxxxx\.top/(\d{4}[\/\-]\d{2}[\/\-]\d{2}[\/\-]\d+)(?:\.html)?')
    SINGLE_CHAPTER = True
    SITE_ENABLE = False

    @classmethod
    def get_comicid_by_url(cls, comicid_or_url):
        if comicid_or_url and isinstance(comicid_or_url, str):
            r = cls.COMICID_PATTERN.search(comicid_or_url)
            comicid = r.group(1) if r else comicid_or_url
            return comicid.replace('/', '-')
        return comicid_or_url

    @property
    def source_url(self):
        return self.get_source_url(self.comicid.replace('-', '/'))

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, 'http://picxxxx.top/%s.html' % comicid)

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = self.comicid
        author = ''
        desc = ''
        image_urls = [img.get('data-src') for img in
                      soup.find('div', {'itemprop': 'articleBody'}).find_all('img')]
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=image_urls[0],
                                       author=author,
                                       source_url=self.source_url)
        book.add_chapter(chapter_number=1, source_url=self.source_url, title='',
                         image_urls=image_urls)
        return book

    def get_chapter_item(self, citem):
        return citem

    def latest(self, page=1):
        if page > 1:
            url = urljoin(self.SITE_INDEX, "/page/%s/" % page)
        else:
            url = self.SITE_INDEX
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for li in soup.find('ul', {'id': 'masonry'}).find_all('li'):
            href = li.a.get('href')
            source_url = urljoin(self.SITE_INDEX, href)
            comicid = self.get_comicid_by_url(source_url)
            name = comicid
            cover_image_url = ''
            if li.img:
                cover_image_url = li.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result
