import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase
from ..exceptions import ChapterNotFound

logger = logging.getLogger(__name__)


class IqiyiCrawler(CrawlerBase):

    SITE = "iqiyi"
    SITE_INDEX = 'https://bud.iqiyi.com/'
    SOURCE_NAME = "爱奇艺漫画"
    LOGIN_URL = SITE_INDEX

    DEFAULT_COMICID = '18yzrlm51h'
    DEFAULT_SEARCH_NAME = '和'
    DEFAULT_TAG = "0"
    COMICID_PATTERN = re.compile(r'/manhua/detail_(.*?)\.html')

    @classmethod
    def get_comicid_by_url(cls, comicid_or_url):
        if comicid_or_url and isinstance(comicid_or_url, str):
            r = cls.COMICID_PATTERN.search(comicid_or_url)
            comicid = r.group(1) if r else comicid_or_url
            return comicid.replace("detail_", "")
        return comicid_or_url

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/manhua/detail_{}.html".format(comicid))

    def get_comicbook_item(self):
        api_url = urljoin(self.SITE_INDEX, "/manhua/catalog/{}/".format(self.comicid))
        data = self.get_json(api_url)['data']
        name = data['title']
        author = data['authorsName']
        desc = data['brief']
        cover_image_url = data['pic']
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)
        for chapter_number, item in enumerate(data['episodes'], start=1):
            episodeId = item['episodeId']
            title = item['episodeTitle']
            url = item['episodeCover']
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title,
                             episodeId=episodeId)
        return book

    def get_chapter_image_urls(self, citem):
        url = urljoin(self.SITE_INDEX, "/manhua/reader/{}_{}.html".format(self.comicid, citem.episodeId))
        soup = self.get_soup(url)
        if soup.find('p', {'class': "pay-title"}):
            raise ChapterNotFound("本章为付费章节，购买后才能继续观看哦～")

        image_urls = []
        for li in soup.find('ul', {"class": "main-container"}).find_all('li'):
            if li.img:
                img_url = li.img.get('data-original') or li.img.get('src')
                image_urls.append(img_url)
        return image_urls
