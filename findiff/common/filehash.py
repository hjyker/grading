import hashlib


def filehash(filepath=None, file=None):
    """生成文件内容 hash, file_content_hash
        filepath: string that file of path
        return: md5 hash
    """

    hash = hashlib.md5()
    fp = None
    chunk = 0

    if filepath:
        fp = open(filepath, 'rb')
    elif file:
        fp = file
    else:
        raise Exception('arguments: filepath or file need at least.')

    while chunk != b'':
        chunk = fp.read(2048)  # read 2048 bytes at a time
        hash.update(chunk)

    if filepath:
        fp.close()

    return hash.hexdigest()
