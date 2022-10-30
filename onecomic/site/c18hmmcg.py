import re
import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class C18hmmcgCrawler(CrawlerBase):

    SITE = "18hmmcg"
    SITE_INDEX = 'https://18h.mm-cg.com/'
    SOURCE_NAME = "18h漫！"
    LOGIN_URL = SITE_INDEX
    R18 = True
    SINGLE_CHAPTER = True

    DEFAULT_COMICID = '18H_6809'
    DEFAULT_SEARCH_NAME = '中文'
    DEFAULT_TAG = "100"
    COMICID_PATTERN = re.compile(r'18h\.mm-cg\.com/(.*?)\.html')

    @property
    def source_url(self):
        return urljoin(self.SITE_INDEX, '%s.html' % self.comicid)

    def get_comicbook_item(self):
        html, soup = self.get_html_and_soup(self.source_url)
        name = soup.find('h1').text.strip()
        author = ''
        desc = ''
        image_urls = re.findall(r'Large_cgurl\[\d+\] = "(.*?)";', html)
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=image_urls[0],
                                       author=author,
                                       source_url=self.source_url)
        book.add_chapter(chapter_number=1, source_url=self.source_url, title='',
                         image_urls=image_urls)
        return book

    def get_chapter_image_urls(self, citem):
        return citem

    def paesr_book_list(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        result = self.new_search_result_item()
        added = set()
        for div in soup.find_all("div", {"class": "post"}):
            href = div.a.get('href')
            comicid = self.get_comicid_by_url(href)
            if comicid in added:
                continue
            added.add(comicid)
            source_url = urljoin(self.SITE_INDEX, href)
            name = div.h3.text.strip()
            cover_image_url = div.a.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def latest(self, page=1):
        if page > 1:
            return self.new_search_result_item()
        html = self.get_html(self.SITE_INDEX)
        return self.paesr_book_list(html)

    TAGS = [
        dict(name='18H漫畫', tag_id='18H_random'),
        dict(name='18H短篇、同人', tag_id='doujin_random'),
    ]

    def get_tags(self):
        tags = self.new_tags_item()
        for i in self.TAGS:
            tags.add_tag(category="分类", name=i['name'], tag=i['tag_id'])
        return tags

    def get_tag_result(self, tag, page=1):
        if page > 1:
            return self.new_search_result_item()
        url = urljoin(self.SITE_INDEX, "/zh/%s/all/index.html" % tag)
        html = self.get_html(url)
        return self.paesr_book_list(html)

    def search(self, name, page, size=None):
        url = urljoin(self.SITE_INDEX, "/zh/doujin_search/all/%s/%s.html" % (name, page))
        html = self.get_html(url)
        return self.paesr_book_list(html)
