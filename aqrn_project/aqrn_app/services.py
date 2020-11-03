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

    return json_object


def get_max_aqi(report):
    max_aqi = -1
    max_aqi_index = -1
    for i in range(len(report)):
        pollutant_aqi = report[i]["AQI"]
        if pollutant_aqi > max_aqi:
            max_aqi = pollutant_aqi
            max_aqi_index = i
    return max_aqi, max_aqi_index


class City:
    def __init__(self, zip_code):
        self.current_json = get_current_aq(zip_code)

        if len(self.current_json) < 1:
            return None

        self.reporting_area = self.current_json[0]["ReportingArea"]

        self.aqi, self.aqi_index = get_max_aqi(self.current_json)

        # Get category name and number if they exist, else they will be set to None
        self.cat_name = self.current_json[self.aqi_index]["Category"].get("Name")
        self.cat_num = self.current_json[self.aqi_index]["Category"].get("Number")

        # TODO: loop through self.current_json and generate self.full_report
        # which is displayed below the form
        # e.g. self.full_report = [[o2, o2 aqi, o2 cat], [pm2.5, pm2.5 aqi, pm2.5 cat]]

        # TODO: get historical data
        # and save as list of dates and AQI ratings
