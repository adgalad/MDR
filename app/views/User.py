
import json
import datetime

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

class User:

  @staticmethod
  def login(request):
    if request.method == "POST":
      form = forms.Login(request.POST)
      if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
          login_auth(request, user)
          return redirect(request.GET.get('next',reverse('index')))
        else:
          messages.error(request, "Bad username or password.")
          
    else:
      form = forms.Login()
   
    if request.GET.get('modal') == '1':
      base = 'modalForm.html'
    else:
      base = 'form.html'
    print(base)
    return render(request, "login.html", {'form': form, 'base':base})    

  @staticmethod
  def editProfile(request):
    if request.method == "POST":
      form = forms.editProfile(request.POST)
      if form.is_valid():
        #print(form.cleaned_data)
        form.save()
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
    else:
      form = forms.editProfile()
    return render(request, "editProfile.html", {'form': form})

  @staticmethod
  def logout(request):
    logout_auth(request)
    return redirect(reverse('index'))

  @staticmethod
  def signup(request):
    if request.method == "POST":
      form = forms.SignUp(request.POST)
      if form.is_valid():
        #print(form.cleaned_data)
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        form.save()
        user = authenticate(username=username, password=password)
        if user is not None:
          login_auth(request, user)
          return redirect(reverse('index'))
    else:
      form = forms.SignUp()
    if request.GET.get('modal') == '1':
      base = 'modalForm.html'
    else:
      base = 'form.html'
    
    return render(request, "SingUp.html", {'form': form, 'base':base})

  @login_required(login_url='/login/')
  @staticmethod
  def addWalletAddress(request):
    message = "Raffle Confirm Wallet %s" %str(datetime.datetime.now())
    if request.method == "POST":
      form = forms.AddWalletAddress(request.POST, instance=request.user)
      if form.is_valid():
        address = form.cleaned_data['wallet_address']
        signature = form.cleaned_data['signature']
        finalMessage = form.cleaned_data['final_message']
        if request.user.message == finalMessage:
          if Dash.verifymessage(address, signature, finalMessage):
            form.save()
            return redirect(reverse('profile'))
          else:
            messages.error(request, "Could not verify signed message. Please try again.")
        else:
          messages.error(request, "The signature has an incorrect message. Please try again.")
      else:
        form = forms.AddWalletAddress(
            initial={'message':message}
          )
        messages.error(request, "jola")
    else:
      request.user.message = message
      request.user.save()
      form =  forms.AddWalletAddress(
            initial={'final_message':message}
          )

    return render(request, "addWalletAddress.html", {'form': form})

  @staticmethod
  def profile(request):
    return render(request, "profile.html")  