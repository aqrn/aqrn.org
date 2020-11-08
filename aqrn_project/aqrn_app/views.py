from typing import List

from django.shortcuts import render
from django.http import HttpResponse
from .services import City, get_populated_city_reports
from .forms import ZipCodeForm
from django.http import Http404


def home(request, zip_param=None):

    # Process form data if POST request or zip is passed via URL
    if request.method == 'POST' or zip_param is not None:

        if request.method == 'POST':
            form = ZipCodeForm(request.POST)
            if form.is_valid():
                zip_code = form.cleaned_data['zip_code']
        else:
            form = ZipCodeForm(initial={'zip_code': zip_param})
            zip_code = zip_param

        try:
            city = City(zip_code)
        except Exception as e:
            raise Http404(e)

        if city.max_aqi != -1:
            body_classes = 'forecast cat' + str(city.max_cat)
            return render(request, 'index.html', {
                'form': form,
                'city': city,
                'body_classes': body_classes,
                'populated_city_reports': get_populated_city_reports(city),
                #'historical_report': city.get_historical_report()
            })
        else:
            return render(request, 'index.html', {
                'form': form,
                'populated_city_reports': get_populated_city_reports()
            })

    else:
        form = ZipCodeForm()

    return render(request, 'index.html', {
        'form': form,
        'populated_city_reports': get_populated_city_reports()
    })

