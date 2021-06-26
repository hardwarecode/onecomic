import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class CopymangaCrawler(CrawlerBase):

    SITE = "copymanga"
    SITE_INDEX = 'https://copymanga.com/'
    SOURCE_NAME = "拷贝漫画"
    LOGIN_URL = SITE_INDEX
    COMICID_PATTERN = re.compile(r'/comic/([_a-zA-Z0-9\-]*)/?')
    DEFAULT_COMICID = 'meiguanxijiejie'
    DEFAULT_SEARCH_NAME = '可爱'
    DEFAULT_TAG = ""
    SITE_ENCODEING = 'utf-8'

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/comic/{}".format(comicid))

    def get_chapters(self, comicid):
        chapters = []
        offset = 0
        limit = 500
        api_url = 'https://api.copymanga.com/api/v3/comic/%s/group/default/chapters?limit=%s&offset=%s'
        url = api_url % (comicid, limit, offset)
        data = self.get_json(url)
        total = data['results']['total']
        chapters.extend(data['results']['list'])
        for i in range(int(total / limit)):
            offset += limit
            url = api_url % (comicid, limit, offset)
            data = self.get_json(url)
            chapters.extend(data['results']['list'])
        return chapters

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        author = ''
        desc = ''
        div = soup.find('div', {'class': 'col-9 comicParticulars-title-right'})
        name = div.h6.text
        cover_image_url = soup.find('div', {'class': 'col-auto comicParticulars-title-left'}).img.get('data-src')
        tag_list = []
        for li in div.find_all('li'):
            text = li.span.text if li.span else ''
            if '作者：' in text:
                author = li.a.text
            elif '狀態：' in text:
                status = li.text.replace('狀態：', '').strip()
            elif '題材：' in text:
                href = li.a.get('href')
                r = re.search(r"/comics\?theme=(.*)", href)
                if r:
                    tag_name = li.a.text.lstrip('#')
                    tag_id = r.group(1)
                    tag_list.append((tag_id, tag_name))
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       status=status,
                                       source_url=self.source_url)
        for tag_id, tag_name in tag_list:
            book.add_tag(name=tag_name, tag=tag_id)
        for chapter_number, item in enumerate(self.get_chapters(self.comicid), start=1):
            uuid = item['uuid']
            url = "https://copymanga.com/comic/%s/chapter/%s" % (self.comicid, uuid)
            title = item['name']
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title,
                             uuid=uuid)
        return book

    def get_chapter_image_urls(self, citem):
        api_url = "https://api.copymanga.com/api/v3/comic/%s/chapter/%s?platform=1&_update=true"
        url = api_url % (self.comicid, citem.uuid)
        data = self.get_json(url)
        image_urls = [i['url'] for i in data['results']['chapter']['contents']]
        return image_urls

    def get_chapter_from_page(self, soup):
        result = self.new_search_result_item()
        for div in soup.find('div', {'class': 'row exemptComic-box'}).find_all('div', recursive=False):
            href = div.a.get('href')
            name = div.find('p', {'class': 'twoLines'}).text
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            cover_image_url = div.img.get('data-src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def latest(self, page=1):
        return self.get_tag_result(tag=None, page=page)

    def get_tags(self):
        url = 'https://copymanga.com/comics'
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        category = '分类列表'
        for a in soup.find('div', {'class': 'classify-right'}).find_all('a'):
            href = a.get('href')
            r = re.search(r"/comics\?theme=(.*)", href)
            if r:
                tag_name = a.dd.text
                tag_id = r.group(1)
                tags.add_tag(category=category, name=tag_name, tag=tag_id)
        return tags

    def get_tag_result(self, tag, page=1):
        limit = 50
        offset = (page - 1) * limit
        if not tag:
            url = 'https://copymanga.com/comics?offset=%s&limit=%s' % (offset, limit)
        else:
            url = 'https://copymanga.com/comics?theme=%s&offset=%s&limit=%s' % (tag, offset, limit)
        soup = self.get_soup(url)
        return self.get_chapter_from_page(soup)

    def search(self, name, page, size=None):
        limit = 20
        offset = (page - 1) * limit
        api_url = "https://copymanga.com/api/kb/web/searchc/comics?offset=%s&platform=2&limit=%s&q=%s&q_type="
        url = api_url % (offset, limit, name)
        data = self.get_json(url)
        result = self.new_search_result_item()
        for i in data['results']['list']:
            comicid = i['path_word']
            name = i['name']
            cover_image_url = i['cover']
            source_url = self.get_source_url(comicid)
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result
