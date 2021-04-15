import os
import re
import logging
import execjs
from urllib.parse import urljoin
from urllib.parse import urlencode
from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)

HERE = os.path.abspath(os.path.dirname(__file__))


class LaimanhuaCrawler(CrawlerBase):

    SITE = "laimanhua"
    SITE_INDEX = 'https://www.laimanhua.com/'
    SOURCE_NAME = "来漫画"

    DEFAULT_COMICID = '10109'
    DEFAULT_SEARCH_NAME = '和'
    DEFAULT_TAG = "rexue"
    COMICID_PATTERN = re.compile(r'/kanmanhua/(\d+)/?')
    SITE_ENCODEING = 'gbk'
    REQUIRE_JAVASCRIPT = True
    BASE64_JS_PATH = os.path.abspath(os.path.join(HERE, '../js/laimanhua_base64.js'))

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/kanmanhua/{}/".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.h1.text.strip()
        desc = soup.find('div', {'id': 'intro1'}).text.strip()

        author = ''
        for p in soup.find('div', {'class': 'info'}).find_all('p', recursive=False):
            if '原著作者：' in p.text:
                author = p.text.replace('原著作者：', '').strip()
        cover_image_url = soup.find('p', {'class': 'cover'}).img.get('src')
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       status='',
                                       source_url=self.source_url)
        for chapter_number, li in enumerate(reversed(soup.find('div', {'id': 'play_0'}).ul.find_all('li')), start=1):
            href = li.a.get('href')
            cid = re.search(r'/\d+/(\d+)\.html', href).group(1)
            url = urljoin(self.SITE_INDEX, href)
            title = li.a.text.strip()
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title,
                             cid=int(cid))
        return book

    def get_chapter_image_urls(self, citem):
        # https://www.laimanhua.com/template/skin4_20110501/js/laimanhuastyle/base64.js
        html = self.get_html(citem.source_url)
        picTree = re.search(r"(var picTree ='.*?';)", html).group(1)
        js_content = open(self.BASE64_JS_PATH, encoding='utf-8').read()

        js_content += '\n'.join([
            picTree,
            'var currentChapterid={};'.format(citem.cid)
        ])
        ctx = execjs.get().compile(js_content, cwd=self.NODE_MODULES)
        urls = ctx.eval(f'getUrlpics()')
        image_urls = []
        for idx, url in enumerate(urls):
            fullurl = ctx.eval(f'getcurpic({idx})')
            image_urls.append(fullurl)
        return image_urls

    def latest(self, page=1):
        url = "https://www.laimanhua.com/kanmanhua/zaixian_recent.html"
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for li in soup.find('div', {'class': 'updateList clearfix'}).ul.find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = li.a.text.strip()
            cover_image_url = ''
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def parser_book_list(self, soup):
        result = self.new_search_result_item()
        for li in soup.find('div', {'id': 'dmList'}).ul.find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = li.a.img.get('alt').strip()
            cover_image_url = li.a.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def search(self, name, page=1):
        if page > 1:
            return self.new_search_result_item()

        search_url = "https://www.laimanhua.com/cse/search/"
        params = {
            'key': name.encode(self.SITE_ENCODEING),
            'page': page,
            'tag': 0
        }
        url = '%s?%s#ysearchs' % (search_url, urlencode(params))
        soup = self.get_soup(url)
        return self.parser_book_list(soup)

    TAGS = [
        dict(name='少年热血', tag_id='rexue'),
        dict(name='武侠格斗', tag_id='gedou'),
        dict(name='科幻魔幻', tag_id='kehuan'),
        dict(name='竞技体育', tag_id='jingji'),
        dict(name='爆笑喜剧', tag_id='gaoxiao'),
        dict(name='侦探推理', tag_id='tuili'),
        dict(name='恐怖灵异', tag_id='kongbu'),
        dict(name='耽美人生', tag_id='danmei'),
        dict(name='少女', tag_id='shaonv'),
        dict(name='恋爱', tag_id='lianai'),
        dict(name='生活', tag_id='shenghuo'),
        dict(name='日韩漫画', tag_id='zaixian_rhmh'),
        dict(name='国产漫画', tag_id='zaixian_dlmh'),
        dict(name='欧美漫画', tag_id='zaixian_ommh'),
        dict(name='港台漫画', tag_id='zaixian_gtmh'),
    ]

    def get_tags(self):
        category = '分类'
        tags = self.new_tags_item()
        for i in self.TAGS:
            name = i['name']
            tag_id = i['tag_id']
            tags.add_tag(category=category, name=name, tag=tag_id)
        return tags

    def get_tag_result(self, tag, page):
        if not tag:
            return self.latest(page=page)
        url = "https://www.laimanhua.com/kanmanhua/%s/%s.html" % (tag, page)
        soup = self.get_soup(url)
        return self.parser_book_list(soup)
