import re
import logging
from urllib.parse import urljoin
import urllib.parse as urlparse

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class BaozimhCrawler(CrawlerBase):

    SITE = "baozimh"
    SITE_INDEX = 'https://www.baozimh.com/'
    SOURCE_NAME = "包子漫画"
    LOGIN_URL = SITE_INDEX

    COMICID_PATTERN = re.compile(r'/comic/([\da-zA-Z_\-]+)/?')
    DEFAULT_COMICID = 'jueshizhanhun-chuanqimanye'
    DEFAULT_SEARCH_NAME = '汉化'
    DEFAULT_TAG = "国漫"

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, '/comic/%s' % comicid)

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.h1.text.strip()
        author = soup.h2.text.strip()
        desc = soup.find('p', {'class': 'comics-detail__desc'}).text.strip()
        cover_image_url = soup.find('div', {'class': 'pure-u-1-1'}).find('amp-img').get('src')
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)
        chapters = []
        chapters.extend(
            soup.find('div', {'id': 'chapter-items'}).find_all('div', recursive=False)
        )
        chapters.extend(
            soup.find('div', {'id': 'chapters_other_list'}).find_all('div', recursive=False)
        )

        for chapter_number, div in enumerate(chapters, start=1):
            href = div.a.get('href')
            source_url = urljoin(self.SITE_INDEX, href)
            title = div.text.strip()
            book.add_chapter(chapter_number=chapter_number,
                             source_url=source_url,
                             title=title)

        for i in soup.find('div', {'class': 'tag-list'}).find_all('span'):
            tag_name = i.text.strip()
            if tag_name:
                book.add_tag(tag=tag_name, name=tag_name)
        return book

    def get_chapter_image_urls(self, citem):
        soup = self.get_soup(citem.source_url)
        image_urls = [img.get('src') for img in soup.find_all('amp-img') if img.get('id', '').startswith('chapter-img')]

        chapter_uri_pattern = citem.source_url.split('/')[-1].replace('.html', '')
        if not re.match(r'\d+_\d+', chapter_uri_pattern):
            parsed = urlparse.urlparse(citem.source_url)
            params = urlparse.parse_qs(parsed.query)
            section_slot = params.get('section_slot')[0] if params.get('section_slot') else 0
            chapter_slot = params.get('chapter_slot')[0] if params.get('chapter_slot') else 0
            chapter_uri_pattern = '%s_%s' % (section_slot, chapter_slot)

        visited = set()
        visited.add(soup.source_url)
        while True:
            try:
                next_url = None
                url = soup.find_all('div', {'class': 'next_chapter'})[-1].a.get('href').split('#')[0]
                s = url.split('/')[-1]
                if url not in visited and s.startswith(chapter_uri_pattern):
                    next_url = url

                if next_url:
                    logger.info('next_url=%s, chapter_uri_pattern=%s', next_url, chapter_uri_pattern)
                    # 0_18.html 0_18_1.html 0_18_2.html 0_19.html
                    soup = self.get_soup(next_url)
                    image_urls.extend([img.get('src') for img in soup.find_all('amp-img') if img.get('id', '').startswith('chapter-img')])
                    visited.add(next_url)
                else:
                    break
            except Exception:
                logger.error('find next_chapter error. url=%s', citem.source_url)
                break

        return image_urls

    def latest(self, page=1):
        if page > 1:
            return self.new_search_result_item()
        url = urljoin(self.SITE_INDEX, "/listnew")
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def get_tags(self):
        url = urljoin(self.SITE_INDEX, "/classify")
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        divs = soup.find_all('div', {'class': 'classify-nav'})
        category = '地区'
        for a in divs[0].find_all('a'):
            href = a.get('href')
            tag = re.search(r'region=(.*?)\&', href).group(1)
            tag_name = a.text.strip()
            if tag_name == '全部':
                continue
            tags.add_tag(category=category, name=tag_name, tag='region_%s' % tag)

        category = '状态'
        for a in divs[1].find_all('a'):
            href = a.get('href')
            tag = re.search(r'state=(.*?)\&', href).group(1)
            tag_name = a.text.strip()
            if tag_name == '全部':
                continue
            tags.add_tag(category=category, name=tag_name, tag='state_%s' % tag)

        category = '题材'
        for a in divs[2].find_all('a'):
            href = a.get('href')
            tag = re.search(r'type=(.*?)\&', href).group(1)
            tag_name = a.text.strip()
            if tag_name == '全部':
                continue
            tags.add_tag(category=category, name=tag_name, tag='type_%s' % tag)

        return tags

    def get_tag_result(self, tag, page=1):
        params = {
            'type': 'all',
            'region': 'all',
            'state': 'all',
            'page': page,
        }
        for t in tag.split(','):
            if t.startswith('type_'):
                params['type'] = t.replace('type_', '')
            elif t.startswith('state_'):
                params['state'] = t.replace('state_', '')
            elif t.startswith('region_'):
                params['region'] = t.replace('region_', '')

        url = urljoin(self.SITE_INDEX, "/classify")
        soup = self.get_soup(url, params=params)
        return self.parse_book_list(soup)

    def parse_book_list(self, soup):
        result = self.new_search_result_item()
        for li in soup.find('div', {'class': 'pure-g'}).find_all('div', recursive=False):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = li.a.get('title').strip()
            cover_image_url = li.a.find('amp-img').get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def search(self, name, page, size=None):
        if page > 1:
            return self.new_search_result_item()
        url = "https://www.baozimh.com/search?q=%s" % name
        soup = self.get_soup(url)
        return self.parse_book_list(soup)
