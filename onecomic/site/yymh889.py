import re
import logging
from urllib.parse import urljoin


from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class Yymh889Crawler(CrawlerBase):

    SITE = "yymh889"
    SITE_INDEX = 'http://yymh889.com/'
    SOURCE_NAME = "歪漫屋"
    LOGIN_URL = SITE_INDEX

    DEFAULT_COMICID = '508'
    DEFAULT_SEARCH_NAME = '甜蜜假期'
    DEFAULT_TAG = ""
    COMICID_PATTERN = re.compile(r'/home/book/index/id/(\d+)')
    SITE_ENCODEING = 'utf-8'

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/home/book/index/id/{}".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        cover_image_url = soup.find('div', {'class': 'cover'}).img.get('webp-src')

        name = soup.find('span', {'class': 'name'}).text.strip()
        author = ''
        for p in soup.find('p', {'class': 'info'}).find_all('p'):
            if '作者: ' in p.label.text:
                author = p.a.text.strip()

        desc = soup.find('p', {'class': 'book-desc'}).text
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)

        total_page = 1
        size = 10
        page = 1
        api_url = 'http://yymh889.com/home/api/chapter_list/tp/{comicid}-1-{page}-{size}'.format(
            comicid=self.comicid,
            page=page,
            size=size
        )
        api_data = self.get_json(api_url)
        total_page = api_data['result']['totalPage']
        chapter_number = 1
        data_list = api_data['result']['list']
        for page in range(2, total_page):
            api_url = 'http://yymh889.com/home/api/chapter_list/tp/{comicid}-1-{page}-{size}'.format(
                comicid=self.comicid,
                page=page,
                size=size
            )
            api_data = self.get_json(api_url)
            data_list.extend(api_data['result']['list'])

        for item in data_list:
            url = urljoin(self.SITE_INDEX, "/home/book/capter/id/{}".format(item['id']))
            title = item['title']
            imagelist = item.get('imagelist')
            image_urls = imagelist.split(',') if imagelist else []
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title,
                             image_urls=image_urls)
            chapter_number += 1
        return book

    def get_chapter_item(self, citem):
        return self.new_chapter_item(chapter_number=citem.chapter_number,
                                     title=citem.title,
                                     image_urls=citem.image_urls,
                                     source_url=citem.source_url)

    def latest(self, page=1):
        url = urljoin(self.SITE_INDEX, '/home/api/getpagex/tp/0-isnew-{}'.format(page))
        api_data = self.get_json(url)
        result = self.new_search_result_item()
        for item in api_data['result'].get('list', []):
            comicid = item['id']
            source_url = self.get_source_url(comicid)
            name = item['title']
            cover_image_url = item['image']
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def search(self, name, page, size=None):
        url = 'http://yymh889.com/home/api/searchk?keyword=%s&type=1&pageNo=%s' % (name, page)
        api_data = self.get_json(url)
        result = self.new_search_result_item()
        for item in api_data['result'].get('list', []):
            comicid = item['id']
            source_url = self.get_source_url(comicid)
            name = item['title']
            cover_image_url = item['image']
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result
