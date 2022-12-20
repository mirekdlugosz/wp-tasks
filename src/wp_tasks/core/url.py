from pathlib import Path
from urllib.parse import urlparse


def get_slug(url):
    parsed = urlparse(url)
    path = Path(parsed.path)
    slug = path.name
    return slug
