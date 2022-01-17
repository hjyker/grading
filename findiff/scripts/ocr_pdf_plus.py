import datetime
import base64
import json
import logging
import io
import shutil
import hashlib
from pathlib import Path

import requests
from PyPDF2 import PdfFileReader, PdfFileWriter
from wand.image import Image

logging.basicConfig(
    level=logging.ERROR,
    filename='/Users/hjyker/Desktop/ocr_req.error.log'
)
logger = logging.getLogger(__name__)


BASE_PATH = Path('/Users/hjyker/Documents/OCR源文件')
RESULTS_PATH = Path('/Users/hjyker/Documents/OCR源文件/ocr_results_220113')


class BaiduOCR:
    def __init__(self):
        self.appid = '25510459'
        self.api_key = 'Ne1WHd5eAKx77VAvl6545XGP'
        self.sec_key = '9TbHdHaEbcubQedMOfPbmxjVshYwfbyl'

    def fetch_token(self):
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.sec_key,
        }
        result = requests.get(
            'https://aip.baidubce.com/oauth/2.0/token', params=params)
        print(result.json()['access_token'])

    def parse_from_pdf(self, pdf_path):
        book_name = pdf_path.name.split('.')[0].strip()
        result_dir_name = RESULTS_PATH / book_name

        if not result_dir_name.exists():
            result_dir_name.mkdir()

        book_meta = {
            'serial_num': hashlib.md5('{0:%Y}{0:%m}{0:%d}{1}'.format(
                datetime.datetime.now(), book_name).encode('utf-8')).hexdigest(),
            'book_name': book_name,
            'authors': [],
            'pdf_pages': 0,
        }

        with pdf_path.open('rb') as pdf_raw:
            pdf_reader = PdfFileReader(pdf_raw)
            book_meta['pdf_pages'] = pdf_reader.numPages

            for page_num, page in enumerate(pdf_reader.pages):
                page_bytes = io.BytesIO()
                pdf_writer = PdfFileWriter()
                pdf_writer.addPage(page)
                pdf_writer.write(page_bytes)
                page_bytes.seek(0)
                with Image(file=page_bytes, resolution=400) as img:
                    try:
                        img = img.convert('PNG')
                        img.alpha_channel = 'remove'
                        img.compression_quality = 90
                        img.transform(f'{img.width}x{img.height}', '50%')

                        img_path = result_dir_name.joinpath(f'{page_num+1}.png')
                        img.save(filename=img_path)
                        img.destroy()
                        yield img_path
                    except Exception as exc:
                        logger.error(f'Error {img_path}')
                        logger.error(exc)

        with result_dir_name.joinpath('meta.json').open('w', encoding='utf-8') as book:
            book.write(json.dumps(book_meta, ensure_ascii=False))

    def store_ocr_data(self, ocr_data, store_path):
        result_txt_path = store_path.parent
        file_name = store_path.name.split('.')[0]

        # 分解内容
        sum_width = 0
        sum_height = 0
        for data in ocr_data['words_result']:
            sum_width += data['location']['width']
            sum_height += data['location']['height']
        writing_mode = 'h' if sum_width >= sum_height else 'v'

        try:
            with open(f'{result_txt_path}/{file_name}-{writing_mode}.txt', 'w', encoding='utf-8') as fp:
                words = [result['words'] for result in ocr_data['words_result']]
                if writing_mode == 'v':
                    words = words[::-1]
                fp.write('\n'.join(words))
                print(f'SUCCESS {store_path}')
        except Exception as exc:
            logger.error(ocr_data)
            logger.error(exc)

    def pdf_to_ocr(self, pdf_path):
        for store_path in self.parse_from_pdf(pdf_path):
            with store_path.open('rb') as image:
                image64 = base64.b64encode(image.read())
                result = requests.post(
                    'https://aip.baidubce.com/rest/2.0/ocr/v1/webimage_loc',
                    headers={'content-type': 'application/x-www-form-urlencoded'},
                    params={
                        'access_token': '24.7a19b816674605dc596b66828371abc5.2592000.1644662341.282335-25510459'},
                    data={'image': image64},
                )

                result = result.json()
                if 'words_result' in result:
                    self.store_ocr_data(result, store_path)
                else:
                    logger.error(store_path)
                    logger.error(result)


if __name__ == '__main__':
    ocr = BaiduOCR()
    ocr.pdf_to_ocr(BASE_PATH / '79--微雨--合併檔--左翻--預ok.pdf')
    # for item in os.listdir(base):
    #     filename = f'{base}/{item}'
    #     if os.path.isfile(filename) and not item.startswith('.'):
    #         print(f'>>>>>> Working {filename}')
    #         ocr.pdf_to_ocr(filename)
    #         shutil.move(filename, f'{base}/finished/{item}')
