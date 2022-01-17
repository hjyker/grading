import time
import hashlib


def get_bulk_id(mix_charts=0):
    chaos = f'{time.time()}.{mix_charts}'
    return hashlib.md5(chaos.encode('utf-8')).hexdigest()
