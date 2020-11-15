from typing import List

from django.shortcuts import render
from .services import City, get_populated_city_reports, get_historical_report, generate_color_key_html
from .forms import ZipCodeForm
from django.http import Http404
from django.shortcuts import redirect


def home(request, zip_param=None):

    # Process form data if POST request or zip is passed via URL
    if request.method == 'POST' or zip_param is not None:

        # Redirect POST submissions so URL updates
        if request.method == 'POST':
            form = ZipCodeForm(request.POST)
            if form.is_valid():
                zip_code = form.cleaned_data['zip_code']
                return redirect(f"/{zip_code}")
            else:
                return redirect("/")

        # Otherwise get zip code from URL
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
                    'historical_report': get_historical_report(city),
                    'color_key': generate_color_key_html()
                })
            else:
                return render(request, 'index.html', {
                    'form': form,
                    'no_result': f'No results found for <strong>{zip_code}</strong>.',
                    'populated_city_reports': get_populated_city_reports(),
                    'color_key': generate_color_key_html()
                })

    else:
        form = ZipCodeForm()

    return render(request, 'index.html', {
        'form': form,
        'populated_city_reports': get_populated_city_reports(),
        'color_key': generate_color_key_html()
    })


def handler404(request, exception=None):
    return redirect('/')

    # form = ZipCodeForm()
    # return render(request, '404.html', {
    #     'form': form,
    #     'populated_city_reports': get_populated_city_reports()
    # })
