import json
import datetime
import requests

from django.http import HttpResponseServerError
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as login_auth
from django.contrib.auth import logout as logout_auth
from app import models, forms
from app.dash import Dash
# Create your views here.

from raffle.settings import DASH_CLI, RPC_SERVER, RPC_PORT, RPC_USER, RPC_PASSWORD, DEFAULT_FROM_EMAIL


def index(request):
  #print(DASH_CLI, RPC_SERVER, RPC_PORT, RPC_USER, RPC_PASSWORD, DEFAULT_FROM_EMAIL)
  raffles = models.Raffle.objects.all()
  return render(request, "index.xhtml", {"raffles":raffles})

def help(request):
    return render(request, "help.html")  
