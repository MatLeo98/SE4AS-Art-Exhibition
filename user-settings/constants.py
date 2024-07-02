from urllib.parse import urlparse

# URLs
settings_url = "http://175.20.0.108:5008"


def parse_url(url):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    return host, port
