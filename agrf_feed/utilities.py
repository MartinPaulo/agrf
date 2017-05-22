import math


def human_readable(size: int) -> str:
    """
    :param size: A byte size that is to be made human readable.
    :returns: A string giving a human readable rendition of the parameter
    """
    if not size:
        return '0B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return f'{s} {size_name[i]}'
