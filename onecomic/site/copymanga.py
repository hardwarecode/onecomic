import re
import binascii
import logging
import json
from urllib.parse import urljoin
from Cryptodome.Cipher import AES
from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


KEY = b"xxxmanga.woo.key"


def add_to_16(value):
    while len(value) % 16 != 0:
        value += b'\x10'
    return value


def aes_encrypt(key, t, iv):
    aes = AES.new(add_to_16(key), AES.MODE_CBC, add_to_16(iv))
    return aes.encrypt(add_to_16(t))


def aes_decrypt(key, t, iv):
    aes = AES.new(add_to_16(key), AES.MODE_CBC, add_to_16(iv))
    return aes.decrypt(t).rstrip(b'\x10')



class CopymangaCrawler(CrawlerBase):

    SITE = "copymanga"
    SITE_INDEX = 'https://copymanga.tv/'
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
        api_url = urljoin(self.SITE_INDEX, "/comicdetail/{}/chapters".format(comicid))
        data = self.get_json(api_url)
        results = data['results']
        s = aes_decrypt(KEY, binascii.a2b_hex(results[16:]), results[:16].encode())
        res = json.loads(re.sub("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]", "", s.decode("utf-8")))
        return res['groups']['default']['chapters']

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
            uuid = item['id']
            url = urljoin(self.SITE_INDEX, "/comic/%s/chapter/%s" % (self.comicid, uuid))
            title = item['name']
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title,
                             uuid=uuid)
        return book

    def get_chapter_image_urls(self, citem):
        html = self.get_html(citem.source_url)
        r = re.search('class="imageData" contentKey="(.*?)"', html)
        contentKey = r.group(1)
        s = aes_decrypt(KEY, binascii.a2b_hex(contentKey[16:]), contentKey[:16].encode())
        res = json.loads(re.sub("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]", "", s.decode("utf-8")))
        image_urls = [i['url'].replace('.c800x.', '.c1500x.') for i in res]
        return image_urls

    def get_chapter_from_page(self, soup):
        result = self.new_search_result_item()
        data_list_str = soup.find('div', {'class': 'row exemptComic-box'}).get('list')
        data_list_str = data_list_str.replace("&#x27;", '"')
        for item in eval(data_list_str):
            comicid = item['path_word']
            name = item['name']
            cover_image_url = item['cover']
            source_url = self.get_source_url(comicid)
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def latest(self, page=1):
        return self.get_tag_result(tag=None, page=page)

    def get_tags(self):
        url = urljoin(self.SITE_INDEX, '/comics')
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
            url = urljoin(self.SITE_INDEX, '/comics?offset=%s&limit=%s' % (offset, limit))
        else:
            url = urljoin(self.SITE_INDEX, '/comics?theme=%s&offset=%s&limit=%s' % (tag, offset, limit))
        soup = self.get_soup(url)
        return self.get_chapter_from_page(soup)

    def search(self, name, page, size=None):
        limit = 20
        offset = (page - 1) * limit
        url = urljoin(
            self.SITE_INDEX,
            "/api/kb/web/searchbc/comics?offset=%s&platform=2&limit=%s&q=%s&q_type=" % (offset, limit, name)
        )


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
