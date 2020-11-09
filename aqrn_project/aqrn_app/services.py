import json
from datetime import datetime, timedelta
import requests
import requests_cache
from django.conf import settings

requests_cache.install_cache(cache_name='air_now_cache', expire_after=1800)


def get_populated_city_reports(main_city=None):
    zip_codes = [10001, 90001, 60007, 77001, 19019, 85001, 91945, 78006, 75001, 94088, 78701]
    if main_city is not None:
        return [City(zip_code) for zip_code in zip_codes if (zip_code != main_city.zip_code)]
    else:
        return [City(zip_code) for zip_code in zip_codes]



def get_realtime_report(zip_code):
    resp_format = 'application/json'
    distance = 25

    url = 'http://www.airnowapi.org/aq/observation/zipCode/current?'
    query_vars = f'format={resp_format}&zipCode={zip_code}' \
                 f'&distance={distance}&API_KEY={settings.AIR_NOW_API_KEY}'

    query_url = url + query_vars
    r = requests.get(query_url)

    json_object = json.loads(r.text)

    return json_object, r.from_cache


class City:
    def __init__(self, zip_code):
        self.realtime_json, self.used_cache = get_realtime_report(zip_code)
        self.max_aqi = -1
        self.max_cat = -1
        self.full_report = []
        self.zip_code = int(zip_code)

        if len(self.realtime_json) < 1:
            return None

        self.reporting_area = self.realtime_json[0]["ReportingArea"]
        self.parse_realtime_report()

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
                cat_name = "Mildly Unhealthy"

            self.full_report.append({"pollutant": pollutant,
                                     "pollutant_aqi": pollutant_aqi,
                                     "cat_num": cat_num,
                                     "cat_name": cat_name})

            if pollutant_aqi > self.max_aqi:
                self.max_aqi = pollutant_aqi
                self.max_cat = cat_num

    # def get_historical_report(self):
    #     historical_report = []
    #     resp_format = 'application/json'
    #     distance = 25
    #     for x in range(8):
    #         date = datetime.now() - timedelta(days=x)
    #         dateStr = datetime.strptime(date, "%Y-%m-%d")
    #
    #         url = 'https://www.airnowapi.org/aq/observation/zipCode/historical/?'
    #         query_vars = f'format={resp_format}&zipCode={self.zip_code}&date={dateStr}' \
    #                          f'&distance={distance}&API_KEY={settings.AIR_NOW_API_KEY}'
    #
    #         query_url = url + query_vars
    #         r = requests.get(query_url)
    #
    #         historic_json = json.loads(r.text)
    #
    #         for i in range(len(historic_json)):
    #             pollutant_aqi = historic_json[i]["AQI"]
    #             cat_num = historic_json[i]["Category"].get("Number")
    #
    #             if cat_num == self.max_cat:
    #                 historical_report.insert(0, [dateStr, pollutant_aqi])
    #
    #     return historical_report
