import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class NsfwpicxCrawler(CrawlerBase):

    SITE = "nsfwpicx"
    SITE_INDEX = 'http://kkoo.icu/'
    SOURCE_NAME = "Nsfwpicx"
    LOGIN_URL = SITE_INDEX
    R18 = True

    DEFAULT_COMICID = '1802'
    DEFAULT_SEARCH_NAME = ''
    DEFAULT_TAG = ""
    COMICID_PATTERN = re.compile(r'kkoo\.icu/(\d+)\.html')
    SINGLE_CHAPTER = True
    SITE_ENABLE = True

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
        return urljoin(self.SITE_INDEX, 'http://kkoo.icu/%s.html' % comicid)

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = self.comicid
        author = ''
        desc = ''
        image_urls = [img.get('data-src') or img.get('src') for img in
                      soup.find('div', {'class': 'entry-content'}).find_all('img')]
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=image_urls[0],
                                       author=author,
                                       source_url=self.source_url)
        book.add_chapter(chapter_number=1, source_url=self.source_url, title='',
                         image_urls=image_urls)
        return book

    def get_chapter_image_urls(self, citem):
        return citem.image_urls

    def latest(self, page=1):
        if page > 1:
            url = urljoin(self.SITE_INDEX, "/page/%s/" % page)
        else:
            url = self.SITE_INDEX
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for a in soup.find_all('a', {'class': 'entry-image'}):
            href = a.get('href')
            source_url = urljoin(self.SITE_INDEX, href)
            comicid = self.get_comicid_by_url(source_url)
            name = comicid
            cover_image_url = a.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def get_tags(self):
        tags = self.new_tags_item()
        for tag, name in [
            ('asia', 'ASIA'),
            ('usa', 'USA'),
            ('cosplay', 'COSPLAY'),
            ('random', 'RANDOM'),
        ]:
            tags.add_tag(category='分类', tag=tag, name=name)
        return tags

    def get_tag_result(self, tag, page):
        if page > 1:
            url = urljoin(self.SITE_INDEX, "/category/%s/page/%s" % (tag, page))
        else:
            url = urljoin(self.SITE_INDEX, "/category/%s" % tag)
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for a in soup.find_all('a', {'class': 'entry-image'}):
            href = a.get('href')
            source_url = urljoin(self.SITE_INDEX, href)
            comicid = self.get_comicid_by_url(source_url)
            name = comicid
            cover_image_url = a.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result
