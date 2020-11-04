import json
from datetime import datetime
import requests
from django.conf import settings


def get_top_10_reports():
    zip_codes = [10001, 90001, 60007, 77001, 19019, 85001, 91945, 78006, 75001, 94088]
    top_10 = []
    for zip_code in zip_codes:
        top_10.append(City(zip_code))

    return top_10


def get_realtime_report(zip_code):
    resp_format = 'application/json'
    distance = 25

    url = 'http://www.airnowapi.org/aq/observation/zipCode/current?'
    query_vars = f'format={resp_format}&zipCode={zip_code}' \
                 f'&distance={distance}&API_KEY={settings.AIR_NOW_API_KEY}'

    query_url = url + query_vars
    r = requests.get(query_url)

    json_object = json.loads(r.text)

    return json_object


class City:
    def __init__(self, zip_code):
        self.realtime_json = get_realtime_report(zip_code)
        self.max_aqi = -1
        self.max_cat = -1
        self.full_report = []

        if len(self.realtime_json) < 1:
            return None

        self.reporting_area = self.realtime_json[0]["ReportingArea"]
        self.parse_realtime_report()

        # TODO: get historical data
        # and save as list of dates and AQI ratings

    def str_max_cat(self):
        return "cat" + str(self.max_cat)

    def parse_realtime_report(self):
        cat_lookup = {
            "Good": 1,
            "Moderate": 2,
            "Unhealthy for Sensitive Groups": 3,
            "Unhealthy": 4,
            "Very Unhealthy": 5,
            "Hazardous": 6,
            1: "Good",
            2: "Moderate",
            3: "Unhealthy for Sensitive Groups",
            4: "Unhealthy",
            5: "Very Unhealthy",
            6: "Hazardous"
        }

        for i in range(len(self.realtime_json)):

            pollutant = self.realtime_json[i]["ParameterName"]
            pollutant_aqi = self.realtime_json[i]["AQI"]

            cat_name = self.realtime_json[i]["Category"].get("Name")
            cat_num = self.realtime_json[i]["Category"].get("Number")
            if cat_name is None:
                cat_name = cat_lookup[int(cat_num)]
            if cat_num is None:
                cat_num = cat_lookup[str(cat_name)]

            # Modify category name
            if cat_name == "Unhealthy for Sensitive Groups":
                cat_name == "Mildly Unhealthy"

            self.full_report.append({"pollutant": pollutant,
                                     "pollutant_aqi": pollutant_aqi,
                                     "cat_num": cat_num,
                                     "cat_name": cat_name})

            if pollutant_aqi > self.max_aqi:
                self.max_aqi = pollutant_aqi
                self.max_cat = cat_num
