from typing import List

from django.shortcuts import render
from .services import City, get_populated_city_reports, get_historical_report, generate_color_key_html
from .forms import ZipCodeForm
from django.http import Http404
from django.shortcuts import redirect
from datetime import datetime


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
                # Unable to init City object
                return render(request, 'index.html', {
                    'no_result': f'<strong>We\'re sorry, something went wrong. </strong>'
                                 'Please check back&nbsp;soon.',
                    'color_key': generate_color_key_html()
                })

            if city.max_aqi != -1:
                # All is good -- city object has data
                body_classes = 'forecast cat' + str(city.max_cat)
                return render(request, 'index.html', {
                    'form': form,
                    'city': city,
                    'body_classes': body_classes,
                    'populated_city_reports': get_populated_city_reports(city),
                    'historical_report': get_historical_report(city),
                    'color_key': generate_color_key_html()
                })
            elif city.response_code == 429:
                # API limit reached
                return render(request, 'index.html', {
                    'no_result': f'The site is temporarily unavailable due to a high volume of requests. '
                                 '<strong>Please try again in an&nbsp;hour.</strong>',
                    'color_key': generate_color_key_html()
                })
            else:
                # API returned with nothing
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


def sitemap(request):
    return render(request, 'sitemap.xml', {
        'today': datetime.today().strftime("%Y-%m-%d")
    }, content_type='application/xml')


def handler404(request, exception=None):
    return redirect('/')

    # form = ZipCodeForm()
    # return render(request, '404.html', {
    #     'form': form,
    #     'populated_city_reports': get_populated_city_reports()
    # })
