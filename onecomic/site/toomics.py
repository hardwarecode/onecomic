import re
import logging
from urllib.parse import urljoin

from ..exceptions import ChapterNotFound
from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class ToomicsCrawler(CrawlerBase):

    SITE = "toomics"
    SITE_INDEX = 'https://toomics.com/'
    SOURCE_NAME = "Toomics"
    LOGIN_URL = SITE_INDEX
    DEFAULT_COMICID = 'sc-5062'
    DEFAULT_SEARCH_NAME = ''
    DEFAULT_TAG = "校园"
    SITE_ENCODEING = 'utf-8'
    COMICID_PATTERN1 = re.compile(r'toomics\.com/(.*?)/webtoon/episode/toon/(\d+)')
    COMICID_PATTERN2 = re.compile(r'toomics\.com/(.*?)/webtoon/detail/code/\d+/ep/\d+/toon/(\d+)')
    SITE_ENABLE = False

    @classmethod
    def get_comicid_by_url(cls, comicid_or_url):
        if comicid_or_url and isinstance(comicid_or_url, str):
            r1 = cls.COMICID_PATTERN1.search(comicid_or_url)
            r2 = cls.COMICID_PATTERN2.search(comicid_or_url)
            if r1:
                comicid = '%s-%s' % r1.groups()
            elif r2:
                comicid = '%s-%s' % r2.groups()
            elif comicid_or_url.isdigit():
                comicid = 'sc-%s' % comicid_or_url
            else:
                comicid = comicid_or_url
            return comicid
        return comicid_or_url

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        a, b = comicid.split('-')
        return 'https://toomics.com/%s/webtoon/episode/toon/%s' % (a, b)

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.find('div', {'class': 'title_content'}).h1.text
        author = soup.find('span', {'class': "writer"}).text
        desc = soup.find('div', {'class': 'title_content'}).h2.text

        tag_list = []
        for tag_name in soup.find('span', {'class': 'type'}).text.strip().split('/'):
            tag_list.append(tag_name.strip())
        style = soup.find('div', {'class': 'inner_ch'}).get('style')
        cover_image_url = re.search(r'url\((.*?)\)', style).group(1)
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)
        chapter_number = 1
        for li in soup.find('ol', {'class': 'list-ep'}).find_all('li'):
            if not li.a:
                continue
            onclick = li.a.get('onclick', '')
            r = re.search(r"(/[a-zA-Z_]+/webtoon/detail/code/\d+/ep/\d+/toon/\d+/?)", onclick)
            if r:
                href = r.group(1)
                title = li.find('div', {'class': 'cell-title'}).strong.text.strip()
                url = urljoin(self.SITE_INDEX, href)
                book.add_chapter(chapter_number=chapter_number,
                                 source_url=url,
                                 title=title)
                chapter_number += 1
        for tag_name in tag_list:
            book.add_tag(name=tag_name, tag=tag_name)
        return book

    def get_chapter_image_urls(self, citem):
        soup = self.get_soup(citem.source_url)
        div = soup.find('div', {'id': 'viewer-img'})
        image_urls = []
        if not div:
            raise ChapterNotFound.from_template(site=self.SITE,
                                                comicid=self.comicid,
                                                chapter_number=citem.chapter_number,
                                                source_url=citem.source_url)
        image_urls = [img.get('data-src') for img in div.find_all('img')]
        return image_urls

    def latest(self, page=1):
        return self.get_tag_result(tag=None, page=page)

    def get_tags(self):
        url = 'https://toomics.com/sc/webtoon/ranking'
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        category = '分类列表'
        for li in soup.find('div', {'class': 'genre_list'}).find_all('li'):
            if not li.a:
                continue
            href = li.a.get('href')
            r = re.search(r'/sc/webtoon/ranking/genre/(\d+)', href)
            if r:
                tag_name = li.a.text.strip()
                tag_id = r.group(1)
                tags.add_tag(category=category, name=tag_name, tag=tag_id)
        return tags

    def get_tag_result(self, tag, page=1):
        if page >= 2:
            return self.new_search_result_item()
        if not tag:
            url = 'https://toomics.com/sc/webtoon/ranking/'
        else:
            url = 'https://toomics.com/sc/webtoon/ranking/genre/%s' % tag
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for li in soup.find('div', {'class': 'list_wrap'}).find_all('li'):
            href = li.a.get('href')
            source_url = urljoin(self.SITE_INDEX, href)
            comicid = self.get_comicid_by_url(source_url)
            name = li.h4.text
            cover_image_url = li.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result
