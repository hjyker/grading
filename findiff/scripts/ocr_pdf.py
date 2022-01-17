import base64
import json
import logging
import os
import re

import pdfplumber
import requests

logging.basicConfig(
    level=logging.INFO,
    filename='/Users/hjyker/Desktop/ocr_req.log'
)
logger = logging.getLogger(__name__)


def refactor_filename():
    filepath = '/Users/hjyker/Documents/OCR源文件'
    file_no = [file.split('-')[0] for file in os.listdir(filepath)]
    print(file_no)


class BaiduOCR:
    def __init__(self):
        self.appid = '24579352'
        self.api_key = '2Shch4yvNvn7SvrOHlLE1f7n'
        self.sec_key = 'gXzzVFKljcY6WReXaWpg9WhrFI2XWYU7'

    def fetch_token(self):
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.sec_key,
        }
        result = requests.get(
            'https://aip.baidubce.com/oauth/2.0/token', params=params)
        print(result.json()['access_token'])

    def parse_from_pdf(self, file):
        base_name = '/Users/hjyker/Documents/OCR源文件/results'
        dir_name = os.path.basename(file).split('.')[0].strip().rstrip('/')
        result_dir_name = f'{base_name}/{dir_name}'

        if not os.path.exists(result_dir_name):
            os.makedirs(result_dir_name)

        is_ltr = dir_name.find('左翻') > -1
        book_meta = {
            'serial_num': re.findall(r'^\d+[\-+0-9]*\d+', dir_name)[0],
            'book_name': dir_name,
            'authors': [],
            'book_pages': 0,
            'writing_mode': 'h' if is_ltr else 'v',
        }

        with pdfplumber.open(file) as pdf:
            book_meta['book_pages'] = len(pdf.pages)
            fp_meta = open(f'{result_dir_name}/meta.json',
                           'w', encoding='utf-8')
            fp_meta.write(json.dumps(book_meta, ensure_ascii=False))
            fp_meta.close()

            for page in pdf.pages:
                for img in page.images:
                    img_name = '%s-%s.jpg' % (img['page_number'], img['name'])
                    page_height = page.height
                    img_box = (img['x0'], page_height - abs(img['y1']),
                               img['x1'], page_height - abs(img['y0']))
                    cropped_page = page.crop(img_box)
                    image_obj = cropped_page.to_image(resolution=600)
                    store_path = f'{result_dir_name}/{img_name}'
                    image_obj.save(store_path, format="JPEG")
                    yield store_path

    def store_ocr_data(self, ocr_data, store_path):
        result_name = os.path.dirname(store_path)
        file_name = os.path.basename(store_path).split('.')[0]
        writing_mode = 'lr' if file_name.find('左翻') > -1 else 'rl'
        try:
            with open(f'{result_name}/{file_name}.txt', 'w', encoding='utf-8') as fp:
                words = [result['words'] for result in ocr_data['words_result']]
                if writing_mode == 'rl':
                    words = words[::-1]
                fp.write('\n'.join(words))
                logger.info(f'SUCCESS {store_path}')
        except Exception as exc:
            logger.error(ocr_data)
            logger.error(exc)

    def pdf_to_ocr(self, file):
        for store_path in self.parse_from_pdf(file):
            with open(store_path, 'rb') as fp:
                image64 = base64.b64encode(fp.read())
                result = requests.post(
                    'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic',
                    headers={'content-type': 'application/x-www-form-urlencoded'},
                    params={
                        'access_token': '24.214ae491cdba8a72327d72c0f4a6c077.2592000.1636273707.282335-24579352'},
                    data={
                        'image': image64,
                        'detect_direction': True,
                        'probability': True,
                    },
                )

                self.store_ocr_data(result.json(), store_path)


if __name__ == '__main__':
    ocr = BaiduOCR()
    # ocr.fetch_token()
    base = '/Users/hjyker/Documents/OCR源文件'
    for item in os.listdir(base):
        filename = f'{base}/{item}'
        if os.path.isfile(filename):
            logging.info(f'Working {filename}')
            ocr.pdf_to_ocr(filename)
