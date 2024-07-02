from urllib.parse import urlparse

# URLs
planner_url = "http://175.20.0.106:5007"
executor_url = "http://175.20.0.107:5006"

# Actions mapping for planner-executor communication
actions = {
    1: ('down', '{measurement} should decrease.'),
    -1: ('up', '{measurement} should increase.'),
    2: ('max-down', '{measurement} has a critical value, emergency decrease.'),
    -2: ('max-up', '{measurement} has a critical value, emergency increase.'),
    3: ('smoke-alarm/off', 'Alarm should be deactivated.'),
    -3: ('smoke-alarm/on', 'Alarm should be activated.')
}


def parse_url(url):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port
    return host, port
