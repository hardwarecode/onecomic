import re
import logging
from urllib.parse import urljoin

from PIL import Image

from ..crawlerbase import CrawlerBase
from ..image import ImageDownloader, retry, ImageDownloadError
from ..utils import ensure_file_dir_exists

logger = logging.getLogger(__name__)


class Yymh889Crawler(CrawlerBase):

    SITE = "yymh889"
    SITE_INDEX = 'http://yymh889.com/'
    SOURCE_NAME = "歪漫屋"
    LOGIN_URL = SITE_INDEX

    DEFAULT_COMICID = '508'
    DEFAULT_SEARCH_NAME = '甜蜜假期'
    DEFAULT_TAG = ""
    COMICID_PATTERN = re.compile(r'/home/book/index/id/(\d+)')
    SITE_ENCODEING = 'utf-8'

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/home/book/index/id/{}".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        cover_image_url = soup.find('div', {'class': 'cover'}).img.get('webp-src')

        name = soup.find('span', {'class': 'name'}).text.strip()
        author = ''
        for p in soup.find('p', {'class': 'info'}).find_all('p'):
            if '作者: ' in p.label.text:
                author = p.a.text.strip()

        desc = soup.find('p', {'class': 'book-desc'}).text
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)

        total_page = 1
        size = 10
        page = 1
        api_url = 'http://yymh889.com/home/api/chapter_list/tp/{comicid}-1-{page}-{size}'.format(
            comicid=self.comicid,
            page=page,
            size=size
        )
        api_data = self.get_json(api_url)
        total_page = api_data['result']['totalPage']
        chapter_number = 1
        data_list = api_data['result']['list']
        for page in range(2, total_page + 1):
            api_url = 'http://yymh889.com/home/api/chapter_list/tp/{comicid}-1-{page}-{size}'.format(
                comicid=self.comicid,
                page=page,
                size=size
            )
            api_data = self.get_json(api_url)
            data_list.extend(api_data['result']['list'])

        for item in data_list:
            url = urljoin(self.SITE_INDEX, "/home/book/capter/id/{}".format(item['id']))
            title = item['title']
            imagelist = item.get('imagelist')
            image_urls = []
            need_patch = False
            if imagelist:
                for url in imagelist.split(','):
                    if url:
                        image_urls.append(url)
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title,
                             image_urls=image_urls or None,
                             need_patch=need_patch)
            chapter_number += 1
        return book

    def get_chapter_item(self, citem):
        if citem.image_urls is not None:
            return citem
        soup = self.get_soup(citem.source_url)
        data = {}
        idx = 0
        for img in soup.find('section', {'class': 'reader-cartoon-chapter'}).find_all('img'):
            r1 = re.search(r'图-(\d+)-(\d+)', img.get('alt'))
            r2 = re.search(r'图-(\d+)', img.get('alt'))
            if r1:
                idx = int(r1.group(1))
            elif r2:
                idx = int(r2.group(1))
            else:
                logger.warn('unknown format. img tag=%s', img)
                continue
            data.setdefault(idx, [])
            data[idx].append(img.get('src'))
        sorted(data.items())
        image_urls = ['||||'.join(i[1]) for i in sorted(data.items(), key=lambda x: x[0])]
        citem.image_urls = image_urls
        return citem

    def latest(self, page=1):
        url = urljoin(self.SITE_INDEX, '/home/api/cate/tp/1-0-2-0-{}'.format(page))
        # url = urljoin(self.SITE_INDEX, '/home/api/getpagex/tp/0-isnew-{}'.format(page))
        api_data = self.get_json(url)
        result = self.new_search_result_item()
        for item in api_data['result'].get('list', []):
            comicid = item['id']
            source_url = self.get_source_url(comicid)
            name = item['title']
            cover_image_url = item['image']
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def search(self, name, page, size=None):
        url = 'http://yymh889.com/home/api/searchk?keyword=%s&type=1&pageNo=%s' % (name, page)
        api_data = self.get_json(url)
        result = self.new_search_result_item()
        for item in api_data['result'].get('list', []):
            comicid = item['id']
            source_url = self.get_source_url(comicid)
            name = item['title']
            cover_image_url = item['image']
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result


class Yymh889ImageDownloader(ImageDownloader):
    SITE = Yymh889Crawler.SITE

    @retry(times=3, delay=1)
    def download_image(self, image_url, target_path, image_pipeline=None, headers=None, **kwargs):
        if self.is_image_exists(target_path):
            return target_path
        session = self.get_session()
        headers = dict(session.headers, **(headers or {}))
        img_list = []
        for image_url in image_url.split('||||'):
            try:
                response = session.get(image_url, timeout=self.timeout, headers=headers, stream=True, **kwargs)
            except Exception as e:
                msg = "img download error: url=%s error: %s" % (image_url, e)
                raise ImageDownloadError(msg) from e

            if response.status_code != 200:
                msg = 'img download error: url=%s status_code=%s' % (image_url, response.status_code)
                raise ImageDownloadError(msg)

            img = Image.open(response.raw)
            img_list.append(img)
        new_img = self.merge_to_one_image(img_list)

        ensure_file_dir_exists(target_path)
        new_img.save(target_path, quality=95)
        return target_path

    def merge_to_one_image(self, img_list):
        # 将图片列表拼接成1张
        if len(img_list) == 1:
            return img_list[0]

        new_width = 0
        new_height = 0
        for img in img_list:
            width, height = img.size
            new_height = height
            new_width += width
        new_img = Image.new(img_list[0].mode, (new_width, new_height))

        w_start = 0
        for img in img_list:
            width, height = img.size
            box = (w_start, 0, w_start + width, new_height)
            new_img.paste(img, box=box)
            w_start += width
        return new_img
