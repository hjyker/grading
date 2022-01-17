import os
import json
import glob
import requests

BASE_PATH = '/Users/hjyker/Documents/OCR源文件/ocr_results_220113'
BASE_URL = 'http://localhost:8080'
DEFAULT_HEADERS = {
    'Authorization': 'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQyMjQ3NTY1LCJqdGkiOiI3MWE4MjQ5MDY0NGQ0OWQ5YWI5NTU5NDUxODRmNGUyMyIsInVzZXJfaWQiOjF9.1webWyvuW2ClnjaeXPGRF5p9uZhPhPV4FexNQe0jyYI',
}


def parse_meta_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as fp:
        meta = json.loads(fp.read())
        print(meta)
        payload = {
            'book_snum': meta['serial_num'],
            'book_name': meta['book_name'],
            'book_pages': meta['pdf_pages'],
        }
        res = requests.post(
            f'{BASE_URL}/order/audit/init_book/',
            data=payload,
            headers=DEFAULT_HEADERS,
        )

        if res.status_code >= 300:
            raise ValueError(file_name)

        res = res.json()
        print(f'SUCCESS {res}')
        return res['id']


def parse_order(dir_name, book_id):
    for file in glob.glob(f'{dir_name}/*.txt'):
        file_name = os.path.basename(file).split('.')[0]
        pdf_page, writing_mode = file_name.split('-')
        img_name = f'{dir_name}/{pdf_page}.png'
        payload = {
            'book_id': (None, book_id),
            'book_page': (None, pdf_page),
            'writing_mode': (None, writing_mode),
            'content_text': '',
            'content_image': open(img_name, 'rb'),
        }

        with open(file, 'r', encoding='utf-8') as text:
            payload['content_text'] = (None, text.read())

        res = requests.post(
            f'{BASE_URL}/order/audit/init_audit/',
            files=payload,
            headers=DEFAULT_HEADERS,
        )

        if res.status_code >= 300:
            print(f'ERROR {res.json()} \n {file} \n {img_name}')

        print(f'SUCCESS {pdf_page}')


def init(dir_name):
    target_name = f'{BASE_PATH}/{dir_name}'

    if os.path.exists(target_name):
        book_id = parse_meta_file(f'{target_name}/meta.json')
        parse_order(target_name, book_id)
    else:
        print(f'ERROR {target_name}')


if __name__ == '__main__':
    init('79--微雨--合併檔--左翻--預ok')
