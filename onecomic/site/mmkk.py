import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class MmkkCrawler(CrawlerBase):

    SITE = "mmkk"
    SITE_INDEX = 'https://www.mmkk.me/'
    SOURCE_NAME = "MMKK"
    LOGIN_URL = SITE_INDEX
    R18 = True

    DEFAULT_COMICID = 'xinggan-4986'
    DEFAULT_SEARCH_NAME = ''
    DEFAULT_TAG = ""
    SITE_ENCODEING = 'utf-8'
    COMICID_PATTERN = re.compile(r'mmkk\.me/([_a-zA-Z0-9]+\/\d+)\.html')
    SINGLE_CHAPTER = True

    @classmethod
    def get_comicid_by_url(cls, comicid_or_url):
        if comicid_or_url and isinstance(comicid_or_url, str):
            r = cls.COMICID_PATTERN.search(comicid_or_url)
            comicid = r.group(1) if r else comicid_or_url
            return comicid.replace('/', '-')
        return comicid_or_url

    @property
    def source_url(self):
        category, _id = self.comicid.split('-')
        return urljoin(self.SITE_INDEX, "/%s/%s.html" % (category, _id))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)

        name = soup.find("meta", {"name": "description"}).get("content", "")
        author = ''
        desc = ''
        soup.find("div", {"id": "masonry"})

        image_urls = self.get_book_image_urls(soup)
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=image_urls[0],
                                       author=author,
                                       source_url=self.source_url)
        book.add_chapter(chapter_number=1, source_url=self.source_url, title='',
                         image_urls=image_urls)
        return book

    def get_book_image_urls(self, soup):
        return [div.img.get('data-original')
                for div in soup.find('div', {'id': 'masonry'}).find_all('div', {'data-fancybox': 'gallery'})]

    def get_chapter_item(self, citem):
        return citem

    def parse_book_list(self, soup):
        result = self.new_search_result_item()
        for div in soup.find('div', {'id': 'masonry'}).find_all('div', recursive=False):
            href = div.a.get('href')
            source_url = urljoin(self.SITE_INDEX, href)
            comicid = self.get_comicid_by_url(source_url)
            name = div.img.get('alt')
            cover_image_url = div.img.get('data-original')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def get_tags(self):
        tags = self.new_tags_item()
        for tag_name, tag_id in [('大学校花', 'xiaohua'),
                                 ('清纯美女', 'qingchun'),
                                 ('性感美女', 'xinggan'),
                                 ('cosplay', 'cosplay'),
                                 ('萝莉腿控', 'meitui'),
                                 ('明星写真', 'mingxing'),
                                 ('旗袍美女', 'qipao'),
                                 ('性感车模', 'chemo'),
                                 ]:
            tags.add_tag(category="分类", name=tag_name, tag=tag_id)
        return tags

    def get_tag_result(self, tag, page):
        if not tag:
            url = self.SITE_INDEX
            if page > 1:
                url += "page/%s/" % page
        else:
            url = urljoin(self.SITE_INDEX, "/category/%s/" % tag)
            if page > 1:
                url += "%s/" % page

        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def latest(self, page=1):
        return self.get_tag_result(tag=None, page=page)
