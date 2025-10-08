# POS/views.py
from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome to the POS Home Page!")

def transactions(request):
    return HttpResponse("POS transaction history goes here.")
