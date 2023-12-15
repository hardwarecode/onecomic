import re
import logging
from urllib.parse import urljoin
from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class KanmanCrawler(CrawlerBase):

    SITE = "kanman"
    SITE_INDEX = 'https://www.kanman.com/'
    SOURCE_NAME = "看漫画"
    LOGIN_URL = SITE_INDEX

    COMICID_PATTERN = re.compile(r'/(\d+)/?')
    DEFAULT_COMICID = '108632'
    DEFAULT_SEARCH_NAME = ''
    DEFAULT_TAG = ""

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, '/%s/' % comicid)

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)

        name = soup.find('h1', {'class': 'title'}).text.strip()
        try:
            author = soup.find('div', {'class': 'username'}).get('title', '')
        except Exception:
            author = ""

        desc = soup.find('div', {'class': 'content'}).text.strip()

        cover_image_url = soup.find('div', {'class': 'img-box'}).img.get('data-src', '')
        cover_image_url = cover_image_url if cover_image_url.startswith('http') else "https:" + cover_image_url

        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)

        for idx, li in enumerate(soup.find('ol', {"id": "j_chapter_list"}).find_all('li'), start=1):
            href = li.a.get('href')
            source_url = urljoin(self.SITE_INDEX, href)
            title = li.a.get('title') or li.a.text.strip()
            book.add_chapter(chapter_number=idx,
                             source_url=source_url,
                             title=title)
        return book

    def get_chapter_item(self, citem):
        api_url = urljoin(self.SITE_INDEX, "/api/getchapterinfov2")
        chapter_newid = citem.source_url.split('/')[-1].split('.')[0]
        params = {
            "product_id": 1,
            "productname": "kmh",
            "platformname": "pc",
            "comic_id": self.comicid,
            "chapter_newid": chapter_newid,
            "isWebp": 1,
            "quality": "high"
        }
        data = self.get_json(api_url, params=params)
        citem.image_urls = data['data']['current_chapter']['chapter_img_list']
        return citem
