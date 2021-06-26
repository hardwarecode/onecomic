import re
import logging
import base64
from urllib.parse import urljoin

from PIL import Image

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class JmzjCrawler(CrawlerBase):

    SITE = "jmzj"
    SITE_INDEX = 'http://jmzj.xyz/'
    SOURCE_NAME = "禁漫之家"
    LOGIN_URL = SITE_INDEX
    R18 = True

    COMICID_PATTERN = re.compile(r'/book/(\d+)\.html')
    DEFAULT_COMICID = '322'
    DEFAULT_SEARCH_NAME = '姐姐'
    DEFAULT_TAG = ""

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, 'book/%s.html' % comicid)

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.h1.text.strip()
        desc = soup.find('p', {'class': 'content'}).text.strip()
        cover_image_url = soup.find('div', {'class': 'comicInfo'})\
            .find('div', {'class': 'img'}).img.get('src')
        if not cover_image_url.startswith('http'):
            cover_image_url = urljoin(self.SITE_INDEX, cover_image_url)
        author = ''
        status = ''
        tag_name = ''
        for span in soup.find('div', {'class': 'ib info'}).find_all('span'):
            text = span.text.strip()
            if '作 者：' in text:
                author = text.replace('作 者：', '').strip()
            elif '狀 態：' in text:
                status = text.replace('狀 態：', '').strip()
            elif '類 別：' in text:
                tag_name = text.replace('類 別：', '').strip()
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       status=status,
                                       source_url=self.source_url)
        for chapter_number, a in enumerate(
                soup.find('div', {'id': 'chapter-list1'}).find_all('a', {'class': 'ib'}), start=1):
            href = a.get('href')
            source_url = urljoin(self.SITE_INDEX, href)
            title = a.text
            book.add_chapter(chapter_number=chapter_number,
                             source_url=source_url,
                             title=title)
        if tag_name:
            book.add_tag(tag=tag_name, name=tag_name)
        return book

    def get_chapter_item(self, citem):
        html = self.get_html(citem.source_url)
        s = re.search(r'var image_urls="(.*?)"', html).group(1)
        scramble_id, aid = re.search(r'note="(.*?)"', html).group(1).split("|")
        image_urls = []
        image_pipelines = []
        for url in base64.b64decode(s.encode()).decode().split(','):
            if not url.startswith('http'):
                url = urljoin(self.SITE_INDEX, url)
            if '.jpg' not in url or int(aid) < int(scramble_id):
                image_pipelines.append(None)
            else:
                image_pipelines.append(self.image_pipeline)
            image_urls.append(url)
        citem.image_urls = image_urls
        citem.image_pipelines = image_pipelines
        return citem

    def image_pipeline(self, image_path):
        img = Image.open(image_path)
        width, height = img.size
        num = 10
        one_piece = int(height / num)
        regions = []
        for i in range(num):
            h_start = (one_piece * i)
            h_end = (one_piece * (i + 1))
            box = (0, h_start, width, h_end)
            region = img.crop(box)
            regions.append(region)
        new_img = Image.new(img.mode, img.size)
        for i, region in enumerate(reversed(regions)):
            h_start = (one_piece * i)
            h_end = (one_piece * (i + 1))
            box = (0, h_start, width, h_end)
            new_img.paste(region, box=box)
        img.close()
        new_img.save(image_path, quality=95)

    def latest(self, page=1):
        if page > 1:
            url = "http://jmzj.xyz/label/update/page/%s.html" % page
        else:
            url = urljoin(self.SITE_INDEX, "/label/update.html")
        soup = self.get_soup(url)
        return self.parser_book_list(soup)

    def parser_book_list(self, soup):
        result = self.new_search_result_item()
        for li in soup.find('div', {'class': 'bookList_3'}).find_all('div', {'class': 'item ib'}):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = li.find('p', {'class': 'title'}).text.strip()
            cover_image_url = urljoin(self.SITE_INDEX, li.img.get('src'))
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def get_tags(self):
        url = urljoin(self.SITE_INDEX, "/booktype/5-----.html")
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        for div in soup.find_all('div', {'class': 'clnav clnav_3'}):
            for span in div.find_all('span'):
                tag_name = span.text.strip()
                tags.add_tag(category='分类', name=tag_name, tag=tag_name)
        return tags

    def get_tag_result(self, tag, page=1):
        if page > 1:
            url = 'http://jmzj.xyz/booktype/5--%s---%s.html' % (tag, page)
        else:
            url = 'http://jmzj.xyz/booktype/5--%s---.html' % (tag)
        soup = self.get_soup(url)
        soup = self.get_soup(url)
        return self.parser_book_list(soup)

    def search(self, name, page, size=None):
        if page > 1:
            url = 'http://jmzj.xyz/search/%s------%s-.html' % (name, page)
        else:
            url = 'http://jmzj.xyz/search/-------.html?wd=%s' % name
        soup = self.get_soup(url)
        return self.parser_book_list(soup)
