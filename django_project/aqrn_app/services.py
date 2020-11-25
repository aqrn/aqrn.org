import json
from datetime import datetime, timedelta, time
import requests
import requests_cache
from django.conf import settings
import random

requests_cache.install_cache(cache_name="air_now_cache", expire_after=3600)


def get_populated_city_reports(main_city=None):
    # Most populated cities
    zip_codes = [10001, 90001, 60007, 77001, 19019, 85006, 91945, 78006, 75001, 94088, 78701]

    # Most polluted cities
    zip_codes += [99703, 15106, 84044, 440101, 93256, 97301]

    random.shuffle(zip_codes)

    populated_cities = [City(zip_code) for zip_code in zip_codes]
    main_city_zip = -1
    if main_city is not None:
        main_city_zip = main_city.zip_code

    return [x for x in populated_cities if x.zip_code != main_city_zip and x.max_aqi != -1]


def get_realtime_report(zip_code):
    """Returns realtime air quality data"""
    resp_format = "application/json"
    distance = 100

    url = "http://www.airnowapi.org/aq/observation/zipCode/current?"
    query_vars = f"format={resp_format}&zipCode={zip_code}" \
                 f"&distance={distance}&API_KEY={settings.AIR_NOW_API_KEY}"

    query_url = url + query_vars
    r = requests.get(query_url)

    json_object = json.loads(r.text)

    # Return JSON response, whether or not the cache was used
    # and the response code
    return json_object, r.from_cache, r.status_code


def get_historical_report(city):
    """Returns peak AQI values from previous days"""
    zip_code = city.zip_code
    historical_report = []

    resp_format = "application/json"
    distance = 100
    url = "https://www.airnowapi.org/aq/observation/zipCode/historical/?"

    # Get reports from recent days
    for x in range(1, 6):
        report_date = (datetime.today() - timedelta(days=x)).strftime("%Y-%m-%d")
        query_vars = f"format={resp_format}&zipCode={zip_code}&date={report_date}T00-0000" \
                     f"&distance={distance}&API_KEY={settings.AIR_NOW_API_KEY}"
        query_url = url + query_vars
        r = requests.get(query_url)
        report = json.loads(r.text)

        # Determine overall AQI value to use for report date
        # by cycling through each pollutant and finding the maximum
        max_aqi = -1
        for i in range(len(report)):
            pollutant_aqi = report[i]["AQI"]
            if pollutant_aqi > max_aqi:
                max_aqi = pollutant_aqi

        # Quit if AQI values are not in report
        if max_aqi == -1:
            return None
        else:
            historical_report.insert(0, {"date": report_date, "aqi": max_aqi})

    # Add realtime AQI to the list
    historical_report.append({"date": datetime.today().strftime("%Y-%m-%d"),
                              "aqi": city.max_aqi})

    # Turn list into a JSON string
    json_string = json.dumps(historical_report)

    # Return a JSON object
    return json.loads(json_string)


def get_categories():
    """Category name/number lookup table"""
    return {
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


def generate_color_key_html():
    """Produces HTML for slide-out color key"""
    categories = get_categories()
    key_html = '<ul id="color-key">'
    for i in range(1, 7):
        key_html += f'<li class="cat{i}"><span>{i}</span>{categories[i]}</li>'

    key_html += '</ul>'
    key_html = key_html.replace("Unhealthy for Sensitive Groups", "Mildly Unhealthy")
    return key_html


def get_advisory(cat_num):
    """Returns health recommendation for category"""
    advisory = {
        # 1: "Air quality is satisfactory, and air pollution poses little or no risk.",
        1: "",
        2: "Air quality is acceptable. However, there may be a risk for some people, particularly those who are "
           "unusually sensitive to air pollution.",
        3: "Members of sensitive groups may experience health effects. The general public is less likely to be "
           "affected.",
        4: "Some members of the general public may experience health effects; members of sensitive groups may "
           "experience more serious health effects.",
        5: "Health alert: The risk of health effects is increased for everyone.",
        6: "Health warning of emergency conditions: everyone is more likely to be affected."
    }
    return advisory.get(cat_num, "")


class City:
    """Requests and stores realtime air quality data for a U.S. city"""
    def __init__(self, zip_code):
        self.realtime_json, self.used_cache, self.response_code = get_realtime_report(zip_code)
        self.max_aqi = -1
        self.max_cat = -1
        self.full_report = []
        self.zip_code = int(zip_code)
        self.advisory = ""

        if self.response_code == 429:
            # API limit reached
            return
        elif len(self.realtime_json) < 1:
            # Report is empty
            return
        else:
            # Get reporting area
            # from first pollutant in the report
            data = self.realtime_json[0]
            self.reporting_area = data.get("ReportingArea")

            if self.reporting_area:
                self.state_code = data.get("StateCode")
                report_hour = data.get("HourObserved")
                report_time_zone = data.get("LocalTimeZone")
                if report_hour and report_time_zone:
                    self.report_time = str(report_hour) + " " + report_time_zone
                self.parse_pollutants()
                self.advisory = get_advisory(self.max_cat)
            else:
                # Something else went wrong -- reporting area should be present
                return

    def parse_pollutants(self):
        """Builds self.full_report list pollutant objects

        This method stores a list of objects,
        one for each pollutant available in the report.
        Each object contains the pollutant name, AQI value,
        category name, and category number.

        In the process, it uses the highest AQI as
        the overall/main AQI value (self.max_aqi)
        """
        cat_lookup = get_categories()

        # Cycle through pollutants in realtime report
        for i in range(len(self.realtime_json)):
            pollutant = self.realtime_json[i]["ParameterName"]
            pollutant_aqi = self.realtime_json[i]["AQI"]

            # Ensure instance contains both category name and number
            cat_name = self.realtime_json[i]["Category"].get("Name")
            cat_num = self.realtime_json[i]["Category"].get("Number")
            if cat_name is None:
                cat_name = cat_lookup[int(cat_num)]
            if cat_num is None:
                cat_num = cat_lookup[str(cat_name)]

            # Modify category name if needed
            if cat_name == "Unhealthy for Sensitive Groups":
                cat_name = "Mildly Unhealthy"

            # Add pollutant info to full report
            self.full_report.append({"pollutant": pollutant,
                                     "pollutant_aqi": pollutant_aqi,
                                     "cat_num": cat_num,
                                     "cat_name": cat_name})

            # Find max pollutant AQI to use as overall AQI
            if pollutant_aqi > self.max_aqi:
                self.max_aqi = pollutant_aqi
                self.max_cat = cat_num
