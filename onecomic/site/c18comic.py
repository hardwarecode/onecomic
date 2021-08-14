import re
import logging
from urllib.parse import urljoin
import functools
import hashlib
import math

from PIL import Image

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class C18comicCrawler(CrawlerBase):

    SITE = "18comic"
    SITE_INDEX = 'https://18comic.vip/'
    SOURCE_NAME = "禁漫天堂"
    LOGIN_URL = SITE_INDEX
    R18 = True

    COMICID_PATTERN = re.compile(r'/album/(\d+)/?')
    DEFAULT_COMICID = '201118'
    DEFAULT_SEARCH_NAME = '騎馬的女孩好想被她騎'
    DEFAULT_TAG = 'CG集'

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/album/{}/".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.find('div', {'itemprop': 'name'}).text.strip()
        author = ''
        desc = ''
        for i in soup.find_all('div', {'class': 'p-t-5 p-b-5'}):
            if '敘述：' in i.text:
                desc = i.text.strip().replace('\n', '').replace('敘述：', '', 1)
        for i in soup.find_all('div', {'class': 'tag-block'}):
            if '作者：' in i.text:
                author = i.text.strip().replace('\n', '').replace('作者：', '', 1)
        cover_image_url = soup.find('img', {'itemprop': 'image'}).get('src')
        res = soup.find('div', {'class': 'episode'})
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)
        for a in soup.find('span', {'itemprop': 'genre'}).find_all('a'):
            tag_name = a.text.strip()
            book.add_tag(name=tag_name, tag=tag_name)
        if not res:
            chapter_number = 1
            url = urljoin(self.SITE_INDEX, '/photo/{}/'.format(self.comicid))
            book.add_chapter(chapter_number=chapter_number, source_url=url, title=str(chapter_number))
        else:
            a_list = res.find_all('a')
            for idx, a_soup in enumerate(a_list, start=1):
                chapter_number = idx
                for i in a_soup.find_all('span'):
                    i.decompose()
                title = a_soup.text.strip().replace('\n', ' ')
                url = a_soup.get('href')
                full_url = urljoin(self.SITE_INDEX, url)
                book.add_chapter(chapter_number=chapter_number, source_url=full_url, title=title)
        return book

    def get_chapter_item(self, citem):
        html, soup = self.get_html_and_soup(citem.source_url)
        scramble_id = re.search(r'var scramble_id = (\d+);', html).group(1)
        aid = re.search(r'var aid = (\d+);', html).group(1)
        readmode = re.search(r'var readmode = "(.*?)";', html).group(1)
        speed = re.search(r'var speed = \'(.*?)\';', html).group(1)
        img_list = soup.find('div', 'row thumb-overlay-albums')\
            .find_all('img', {'id': re.compile(r'album_photo_\d+')})
        image_urls = []
        image_pipelines = []
        for img_soup in img_list:
            url = img_soup.get('data-original')
            if not url:
                url = img_soup.get('src')
            image_urls.append(url)
            l = img_soup.parent.get('id').split('.')[0]
            func = functools.partial(
                self.scramble_image,
                aid=aid, scramble_id=scramble_id, readmode=readmode, speed=speed, image_url=url, l=l)
            image_pipelines.append(func)
        citem.image_pipelines = image_pipelines
        citem.image_urls = image_urls
        return citem

    def scramble_image(self, image_path, image_url, aid, scramble_id, readmode, speed, l):
        """
        JavaScript 语法：  context.drawImage(img,sx,sy,swidth,sheight,x,y,width,height);
        参数值
        参数  描述
        img 规定要使用的图像、画布或视频。
        sx  可选。开始剪切的 x 坐标位置。
        sy  可选。开始剪切的 y 坐标位置。
        swidth  可选。被剪切图像的宽度。
        sheight 可选。被剪切图像的高度。
        x   在画布上放置图像的 x 坐标位置。
        y   在画布上放置图像的 y 坐标位置。
        width   可选。要使用的图像的宽度（伸展或缩小图像）。
        height  可选。要使用的图像的高度（伸展或缩小图像）。
        """
        if readmode == 'read-by-page':
            return
        if '.jpg' not in image_url or int(aid) < int(scramble_id) or speed == '1':
            return
        img = Image.open(image_path)
        new_img = Image.new(img.mode, img.size)
        width, height = img.size
        i = height
        d = width
        o = d
        s = self.get_num(aid, l)
        r = int(i % s)
        logger.debug('scramble_image aid=%s, scramble_id=%s, readmode=%s, speed=%s, l=%s s=%s', aid, scramble_id, readmode, speed, l, s)
        for m in range(s):
            c = math.floor(float(i) / s)
            g = c * m
            h = i - c * (m + 1) - r
            if 0 == m:
                c += r
            else:
                g += r
            # a.drawImage(e, 0, h, o, c,   0, g, o, c)
            box = (0, h, width, h + c)
            new_box = (0, g, o, g + c)
            region = img.crop(box)
            new_img.paste(region, box=new_box)
        img.close()
        new_img.save(image_path, quality=95)

    def get_num(self, e, t):
        e = int(e)
        a = 10
        if e >= 268850:
            n = str(e) + t
            n = ord(hashlib.md5(str(n).encode()).hexdigest()[-1])
            n %= 10
            ret_map = {
                0: 2,
                1: 4,
                2: 6,
                3: 8,
                4: 10,
                5: 12,
                6: 14,
                7: 16,
                8: 18,
                9: 20,
            }
            return ret_map[n]
        return a

    def search(self, name, page=1, size=None):
        url = urljoin(
            self.SITE_INDEX,
            '/search/photos?search_query={}&page={}'.format(name, page)
        )
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for div in soup.find_all('div', {'class': 'thumb-overlay'}):
            comicid = div.a.get('id').split('_')[-1]
            name = div.img.get('alt')
            cover_image_url = div.img.get('data-original')
            source_url = self.get_source_url(comicid)
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def latest(self, page=1):
        url = urljoin(self.SITE_INDEX, '/albums')
        url += '?o=mr&page=%s' % page
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for div in soup.find_all('div', {'class': 'thumb-overlay-albums'}):
            comicid = div.a.get('id').split('_')[-1]
            name = div.img.get('alt')
            cover_image_url = div.img.get('data-original')
            source_url = self.get_source_url(comicid)
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def get_tags(self):
        url = urljoin(self.SITE_INDEX, "/theme/")
        soup = self.get_soup(url)

        div_list = soup.find('div', {'id': 'wrapper'}).find('div', {'class': 'container'})\
            .find_all('div', {'class': 'row'})
        tags = self.new_tags_item()
        for div in div_list:
            h4 = div.h4
            if not h4:
                continue
            category = h4.text
            for li in div.find_all('li'):
                name = li.a.text
                tags.add_tag(category=category, name=name, tag=name)
        return tags

    def get_tag_result(self, tag, page=1):
        return self.search(name=tag, page=page)

    def login(self):
        self.selenium_login(login_url=self.LOGIN_URL,
                            check_login_status_func=self.check_login_status)

    def check_login_status(self):
        session = self.get_session()
        if session.cookies.get("remember", domain=".18comic.vip"):
            return True
