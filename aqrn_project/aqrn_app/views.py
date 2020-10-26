from django.shortcuts import render
from django.http import HttpResponse
from .services import get_current_aq


def home(request):
    report = get_current_aq(98121)
    return HttpResponse(report, content_type='application_json')
