from typing import List

from django.shortcuts import render
from django.http import HttpResponse
from .services import City, get_populated_city_reports
from .forms import ZipCodeForm
from django.http import Http404


def home(request):
    # Process form data if POST request
    populated_city_reports = get_populated_city_reports()
    if request.method == 'POST':

        form = ZipCodeForm(request.POST)

        if form.is_valid():
            zip_code = form.cleaned_data['zip_code']

            try:
                city = City(zip_code)
            except Exception as e:
                raise Http404(e)

            if city.max_aqi != -1:
                body_classes = 'forecast cat' + str(city.max_cat)
                return render(request, 'index.html', {
                    'form': form,
                    'zip_code': zip_code,
                    'city': city,
                    'body_classes': body_classes,
                    'populated_city_reports': populated_city_reports,
                    #'historical_report': city.get_historical_report()
                })
            else:
                return render(request, 'index.html', {
                    'form': form,
                    'populated_city_reports': populated_city_reports
                })

    else:
        form = ZipCodeForm()

    return render(request, 'index.html', {
        'form': form,
        'populated_city_reports': populated_city_reports
    })

