import json
import datetime
import requests

from django.http import HttpResponseServerError
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from app import models, forms
from app.dash import Dash


def index(request):
  #print(DASH_CLI, RPC_SERVER, RPC_PORT, RPC_USER, RPC_PASSWORD, DEFAULT_FROM_EMAIL)
  tx = models.Transaction.object.all()[:15]
  return render(request, "index.xhtml", {"transactions":tx})

def help(request):
    return render(request, "help.html")  


def terms(request):
    return render(request, 'terms.html')

def conditions(request):
    return render(request, 'conditions.html')

def password_reset(request):
 if request.method == "POST":
   form = ChangeEmailForm(request.POST)
   if form.is_valid():
     email = form.cleaned_data.get('email')
     try: user = User.objects.get(email=email)
     except: user = None

     if user is None:
       messages.error(request,'El correo que ingresó no se encuentra registrado.', extra_tags="alert-warning")
       return render(request, 'registration/password_reset_form.html', {'form': form})
     elif not user.is_active:
       messages.error(request,'La cuenta asociada a este correo no se encuentra activa.', extra_tags="alert-warning")
       return render(request, 'registration/password_reset_form.html', {'form': form})

 return auth_views.password_reset(request, password_reset_form=MyPasswordResetForm)