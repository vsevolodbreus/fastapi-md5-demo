import hashlib


def get_md5_hash(file_path: str, block_size: int = 4096) -> str:
    with open(file_path, "rb") as file_obj:
        md5_hash = hashlib.md5()
        for chunk in iter(lambda: file_obj.read(block_size), b""):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()
