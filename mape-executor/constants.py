from urllib.parse import urlparse

# InfluxDB configurarion
bucket = "artexhibition"
org = "univaq"
token = "m1rcn8P_qoLuUWHyMezmNb8L-dcq2H4YLWT5i87Uhk4IvpLPR9lt8Q576UrRgLowsCE8Yw1mg9KUBWC9ImSIMQ=="

# URLs
mqtt_url = "175.20.0.100"
influx_url = "http://175.20.0.102:8086"
executor_url = "http://175.20.0.107:5006"


def parse_url(url):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    return host, port
