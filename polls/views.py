from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime

def index(request):
    now = datetime.now()

    current_time = now.strftime("%H:%M")

    return HttpResponse("Hello, Hannah. It's {}. You should go for a run now!.".format(current_time))
