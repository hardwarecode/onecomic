import re
import logging
import json
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class C2feimhCrawler(CrawlerBase):

    SITE = "2feimh"
    SITE_INDEX = 'https://www.2feimh.com/'
    SOURCE_NAME = "爱飞漫画"

    DEFAULT_COMICID = 'bcdrbzx'
    DEFAULT_SEARCH_NAME = '和'
    DEFAULT_TAG = ""
    COMICID_PATTERN = re.compile(r'/(.*?)/?')

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/{}/".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.h1.get('title')
        self.data_comic_id = soup.h1.get('data-comic-id')

        desc = soup.find('p', {'class': 'desc-content'}).text.strip()
        author = ''
        cover_image_url = soup.find('div', {'class': 'detail-cover'}).img.get('data-src')
        if not cover_image_url.startswith('http'):
            cover_image_url = 'https:' + cover_image_url
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       status='',
                                       source_url=self.source_url)
        for chapter_number, li in enumerate(soup.find('ol', {'id': 'j_chapter_list'}).find_all('li'), start=1):
            href = li.a.get('href')
            url = urljoin(self.SITE_INDEX, href)
            title = li.a.text.strip()
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title)
        return book

    def get_chapter_image_urls(self, citem):
        html = self.get_html(citem.source_url)
        s = re.search(r'<script>window\.\$definitions=(.*?)</script>', html).group(1)

        # api_url = 'https://www.2feimh.com/api/getchapterinfo?comic_id=%s&chapter_newid=%s' % (
        #     self.data_comic_id, citem.chapter_number
        # )
        # data = self.get_json(api_url)
        rule = re.search(r'rule:"(.*?)"', s).group(1)
        chapter_domain = re.search(r'chapter_domain:"(.*?)"', s).group(1)
        end_num = re.search(r'end_num:(\d+)', s).group(1)
        image_urls = []
        for i in range(1, int(end_num) + 1):
            image_url = urljoin('https://%s/' % chapter_domain, rule.replace('$$', str(i))) + '-kmh.middle.webp'
            image_urls.append(image_url)
        return image_urls
