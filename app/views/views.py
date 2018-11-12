import json
import datetime
import requests

from django.http import HttpResponseServerError
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from app import models, forms
from app.dash import Dash


def index(request):
  #print(DASH_CLI, RPC_SERVER, RPC_PORT, RPC_USER, RPC_PASSWORD, DEFAULT_FROM_EMAIL)
  tx = models.Transaction.objects.all()[:15]
  raffles = models.Raffle.objects.filter(drawDate__gt=timezone.now()).exclude(is_active=False)[:10]
  return render(request, "index.xhtml", {"raffles":raffles,"transactions":tx})

def help(request):
    return render(request, "help.html")  


def terms(request):
    return render(request, 'terms.html')

def conditions(request):
    return render(request, 'conditions.html')

def error_500(request):
    return render(request, '500.html')
