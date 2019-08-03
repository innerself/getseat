import hashlib


def calculate_md5(init_string: str) -> str:
    return hashlib.md5(init_string.encode()).hexdigest()


def mocked_get_raw_page(url):
    file_name = f'{calculate_md5(url)}.txt'

    with open(file_name, 'r') as file:
        page_source = file.read()

    return page_source


def read_page_from_file(_):
    def wrapper(*args, **kwargs):
        page_source = mocked_get_raw_page(*args, **kwargs)

        return page_source

    return wrapper
