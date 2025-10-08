from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome to the Deliveries Home Page!")

def list_deliveries(request):
    return HttpResponse("Here is the list of deliveries.")
