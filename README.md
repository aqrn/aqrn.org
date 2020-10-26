# aqrn.org

## About the project

aqrn.org is an air quality monitoring website in development for a CSC 484 Software Engineering group project at Dakota State University (Fall 2020).

## Documentation

[Project documentation](https://github.com/aqrn/aqrn.org/wiki) can be found in the repo wiki.

## Developer instructions

#### Install requirements
Create a virtual environment in the project root and activate, then install the requirements.
```sh
pip install -r requirements.txt
```
#### Add local settings
Copy and rename **local_settings_template.py** to **local_settings.py**, and fill in the global variables:

`SECRET_KEY` = Django’s secret key used by the project

`AIR_NOW_API_KEY` = API keys available at airnowapi.org

#### Run the app

```sh
python manage.py runserver
```

Navigate to http://localhost:8000/

