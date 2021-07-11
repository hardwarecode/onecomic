import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class MyfcomicCrawler(CrawlerBase):

    SITE = "myfcomic"
    SITE_INDEX = 'http://www.myfcomic.com/'
    SOURCE_NAME = "漫番漫画"
    LOGIN_URL = SITE_INDEX

    DEFAULT_COMICID = '327'
    DEFAULT_SEARCH_NAME = '的'
    DEFAULT_TAG = "fenlei_0"
    COMICID_PATTERN = re.compile(r'/comic/(\d+)')

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/comic/{}".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.find('div', {'class': 'comic_detail'}).find('p', {'class': 'p1'}).text.strip()
        author = ''
        status = ''
        for span in soup.find('div', {'class': 'comic_detail'}).find('div', {'class': 'p2'})\
                .find_all('span', recursive=False):
            if '作者：' in span.text:
                author = span.text.replace('作者：', '').strip()
            elif '状态：' in span.text:
                status = span.text.replace('状态：', '').strip()
        desc = soup.find('div', {'class': 'comic_detail'}).find('p', {'class': 'p3'}).text.strip()
        cover_image_url = soup.find('div', {'class', 'comic_head'}).img.get('src')
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       status=status,
                                       source_url=self.source_url)
        for a in soup.find('span', {'class': 'p2Classify'}).find_all('a'):
            href = a.get('href')
            tag = re.search(r'/classify/(\d+)', href).group(1)
            name = a.text.strip()
            book.add_tag(name=name, tag=tag)

        li_list = soup.find('div', {'class': 'comic_chapter_list'}).find_all('p', {'class': 'comic_chapter_item'})
        items = {}
        for chapter_number, li in enumerate(li_list, start=1):
            href = li.a.get('href')
            url = urljoin(self.SITE_INDEX, href)
            title = li.a.text.strip()
            cid = re.search(r'/cview\?id=\d+&cid=(\d+)', href).group(1)
            items[cid] = dict(source_url=url,
                              title=title,
                              cid=cid)

        size = 40
        if len(items) >= size:
            page = 2
            while True:
                api = 'https://user.myfcomic.com/api/comic/getchapterlist'
                params = {
                    "comic_id": str(self.comicid),
                    "platform": "5",
                    "size": str(size),
                    "page": page
                }
                response = self.send_request('POST', api, params=params)
                data = response.json()['data']['list']
                for item in data:
                    cid = str(item['id'])
                    title = item['chapter_title']
                    url = urljoin(self.SITE_INDEX, '/cview?id=%s&cid=%s' % (self.comicid, cid))
                    items[cid] = dict(source_url=url,
                                      title=title,
                                      cid=cid)
                if len(data) < size:
                    break
                page += 1

        for chapter_number, item in enumerate(sorted(items.values(), key=lambda x: int(x['cid'])), start=1):
            book.add_chapter(chapter_number=chapter_number,
                             source_url=item['source_url'],
                             title=item['title'],
                             cid=item['cid'])
        return book

    def get_chapter_image_urls(self, citem):
        api = 'https://codetest.myfcomic.com/api/getchapterinfo?comic_id=%s&chapter_id=%s&platform=5&netstatus=1' % (
            self.comicid, citem.cid)
        data = self.get_json(api)
        image_urls = [item['name'] for item in data['data']['images']]
        return image_urls

    def latest(self, page=1):
        api = 'https://codetest.myfcomic.com/api/getcatlist?platform=5&theme_id=0&region_id=0&publisher_id=0&progress=0&order_hot=0&new_shelves=0&update_time=1'
        if page > 1:
            return self.new_search_result_item()
        data = self.get_json(api)
        result = self.new_search_result_item()
        for item in data['data']:
            comicid = item['id']
            source_url = self.get_source_url(comicid)
            name = item['title']
            cover_image_url = item['cover']
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def get_tags(self):
        url = urljoin(self.SITE_INDEX, "/classify")
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        for div in soup.find_all('div', {'class': 'classify_screen_box_tit'}):
            if div.p.text.strip() == '分类':
                for idx, span in enumerate(div.find_all('span')):
                    tags.add_tag(category='分类', tag='fenlei_%s' % idx, name=span.text.strip())
            elif div.p.text.strip() == '地区':
                for idx, span in enumerate(div.find_all('span')):
                    tags.add_tag(category='地区', tag='diqu_%s' % idx, name=span.text.strip())
            elif div.p.text.strip() == '出版社':
                for idx, span in enumerate(div.find_all('span')):
                    tags.add_tag(category='出版社', tag='chubanshe_%s' % idx, name=span.text.strip())
            elif div.p.text.strip() == '进度':
                for idx, span in enumerate(div.find_all('span')):
                    tags.add_tag(category='进度', tag='jindu_%s' % idx, name=span.text.strip())
        return tags

    def get_tag_result(self, tag, page=1):
        if page > 1:
            return self.new_search_result_item()
        api = 'https://codetest.myfcomic.com/api/getcatlist'
        params = {
            'theme_id': 0,
            'region_id': 0,
            'publisher_id': 0,
            'progress': 0,
            'platform': 5,
            'order_hot': 1,
            'new_shelves': 0,
            'update_time': 0

        }
        for t in tag.split(','):
            if t.startswith('fenlei_'):
                params['theme_id'] = t.replace('fenlei_', '')
            elif t.startswith('diqu_'):
                params['region_id'] = t.replace('diqu_', '')
            elif t.startswith('chubanshe_'):
                params['publisher_id'] = t.replace('chubanshe_', '')
            elif t.startswith('jindu_'):
                params['progress'] = t.replace('jindu_', '')
        data = self.get_json(api, params=params)
        result = self.new_search_result_item()
        for item in data['data']:
            comicid = item['id']
            source_url = self.get_source_url(comicid)
            name = item['title']
            cover_image_url = item['cover']
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def search(self, name, page=1, size=None):
        if page > 1:
            return self.new_search_result_item()
        api = 'https://pay.myfcomic.com/api/search/composite'
        params = {"title": name, "platform": "5"}
        response = self.send_request('POST', api, params=params)
        result = self.new_search_result_item()
        for item in response.json()['data']['comic']['list']:
            comicid = item['id']
            source_url = self.get_source_url(comicid)
            name = item['title']
            cover_image_url = item['cover']
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result
