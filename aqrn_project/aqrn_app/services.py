import json
from datetime import datetime
import requests
from django.conf import settings


def get_current_aq(zip_code):
    today = datetime.today().strftime('%Y-%m-%d')
    resp_format = 'application/json'
    distance = 25

    url = 'http://www.airnowapi.org/aq/observation/zipCode/current?'
    query_vars = f'format={resp_format}&zipCode={zip_code}' \
                 f'&distance={distance}&API_KEY={settings.AIR_NOW_API_KEY}'

    query_url = url + query_vars
    r = requests.get(query_url)

    json_object = json.loads(r.text)

    json_formatted_str = json.dumps(json_object, indent=2)

    return json_formatted_str

