# InfluxDB configurarion
bucket = "artexhibition"
org = "univaq"
token = "m1rcn8P_qoLuUWHyMezmNb8L-dcq2H4YLWT5i87Uhk4IvpLPR9lt8Q576UrRgLowsCE8Yw1mg9KUBWC9ImSIMQ=="

# URLs
mqtt_url = "localhost"
influx_url = "http://localhost:8086"
settings_url = "http://localhost:5008"
planner_url = "http://localhost:5007"
executor_url = "http://localhost:5006"

# Actions mapping for planner/executor
actions = {
    1: ('down', '{measurement} should decrease.'),
    -1: ('up', '{measurement} should increase.'),
    2: ('max-down', '{measurement} has a critical value, emergency decrease.'),
    -2: ('max-up', '{measurement} has a critical value, emergency increase.'),
    3: ('smoke-alarm/off', 'Alarm should be deactivated.'),
    -3: ('smoke-alarm/on', 'Alarm should be activated.')
}