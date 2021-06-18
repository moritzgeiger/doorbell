from django.http import HttpResponse, response
from django.template import loader
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
