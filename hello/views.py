from django.shortcuts import render
from django.http import HttpResponse
#from django.utils import simplejson

from .models import Greeting
import requests
# Create your views here.
def index(request):
    # r = requests.get('http://httpbin.org/status/418')
    # print(r.text)
    # return HttpResponse('<pre>' + r.text + '</pre>')
    context = {'Tokyo': [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 40, 23.3, 18.3, 13.9, 9.6]}
    return render(request, "index.html", context)

def view_teapot(request):
    context = {'data': [
                       {'y': 107, 'color':'red'},
                       {'y':31, 'color':'red'},
                       {'y':635},
                       {'y':203, 'color':'green'},
                       {'y':2}
                   ]}
    return render(request, "chart.html", context)
    
def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()
    return render(request, "db.html", {"greetings": greetings})
