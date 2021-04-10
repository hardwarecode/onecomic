import re
import logging
import json
from urllib.parse import urljoin
from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class YkmhCrawler(CrawlerBase):

    SITE = "ykmh"
    SITE_INDEX = 'https://www.ykmh.com/'
    SOURCE_NAME = "优酷漫画"

    DEFAULT_COMICID = 'shijizhiling'
    DEFAULT_SEARCH_NAME = '和'
    DEFAULT_TAG = ""
    COMICID_PATTERN = re.compile(r'/manhua/(.*?)/([_a-zA-Z0-9\-]*)/?')

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/manhua/{}/".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.h1.text.strip()
        desc = soup.find('p', {'class': 'comic_deCon_d'}).text.strip()

        author = ''
        status = ''
        for li in soup.find('ul', {'class': 'comic_deCon_liO'}).find_all('li'):
            if '作者：' in li.text:
                author = li.a.text.strip()
            elif '状态：':
                status = li.a.text.strip()
        cover_image_url = soup.find('div', {'class': 'comic_i_img'}).img.get('src')
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       status=status,
                                       source_url=self.source_url)
        li_list = soup.find('ul', {'id': 'chapter-list-1'}).find_all('li')
        for chapter_number, li in enumerate(reversed(li_list), start=1):
            href = li.a.get('href')
            url = urljoin(self.SITE_INDEX, href)
            title = li.find('span', {'class': 'list_con_zj'}).text.strip()
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title)
        return book

    def get_chapter_image_urls(self, citem):
        html = self.get_html(citem.source_url)
        s = re.search(r"var chapterImages = (\[.*?\]);", html).group(1)
        prefix = 'http://pic.w1fl.com'
        image_urls = [prefix + i for i in json.loads(s)]
        return image_urls

    def parser_book_list(self, soup):
        result = self.new_search_result_item()
        for li in soup.find('ul', {'class': 'list_con_li'}).find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = li.a.img.get('alt') or li.a.get('title')
            name = name.strip()
            cover_image_url = li.a.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def latest(self, page=1):
        url = "https://www.ykmh.com/update/"
        if page > 1:
            url = "https://www.ykmh.com/update/%s/" % page
        soup = self.get_soup(url)
        return self.parser_book_list(soup)

    def search(self, name, page=1):
        url = "https://www.ykmh.com/search/?keywords=%s&page=%s" % (name, page)
        soup = self.get_soup(url)
        return self.parser_book_list(soup)
