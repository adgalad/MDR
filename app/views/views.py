import json
import datetime
import requests

from django.http import HttpResponseServerError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from app import models, forms
from app.dash import Dash

def index(request):
  tx = models.Transaction.objects.all()[:15]
  raffles = models.Raffle.objects.filter(drawDate__gt=timezone.now()).exclude(is_active=False)[:10]
  return render(request, "index.xhtml", {"raffles":raffles,"transactions":tx})

def help(request):
    return render(request, "help.html")  


def terms(request):
    return render(request, 'terms.html')

def conditions(request):
    return render(request, 'conditions.html')

def handler400(request):
   title = "400"
   message = "Bad request. Try again."
   response = render(request, 'error.html', {"title":title, "message":message})
   response.status_code = 400
   return response

def handler403(request):
   title = "403"
   message = "Your don't have permission to see what you requested."
   response = render(request, 'error.html', {"title":title, "message":message})
   response.status_code = 403
   return response

def handler404(request):
   title = "404"
   message = "We couldn't find what you were looking for."
   response = render(request, 'error.html', {"title":title, "message":message})
   response.status_code = 404
   return response

def handler500(request):
   title = "500"
   response = render(request, '500.html')
   response.status_code = 500
   return response
