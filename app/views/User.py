
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
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from app import models, forms
from app.helpers import EmailThread
from django.template import loader
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
          return redirect(request.GET.get('next',reverse('home')))
        else:
          messages.error(request, "Bad username or password.")
          
    else:
      form = forms.Login()
   
    if request.GET.get('modal') == '1':
      base = 'modalForm.html'
    else:
      base = 'form.html'
    return render(request, "login.html", {'form': form, 'base':base})    

  @staticmethod
  @login_required(login_url='/login/')
  def editProfile(request):
    if request.method == "POST":
      form = forms.EditProfile(request.POST, instance=request.user)
      if form.is_valid():
        form.save()
        messages.success(request, "Email was changed successfully.", extra_tags="alert-success")
        return redirect(reverse('profile'))
    else:
      form = forms.EditProfile(instance=request.user)
      passwordForm = PasswordChangeForm(user=request.user)
    if request.GET.get('modal') == '1':
      base = 'modalForm.html'
    else:
      base = 'form.html'
    return render(request, "editProfile.html", {'form': form, 'passwordForm':passwordForm,'base':base})

  @staticmethod
  @login_required(login_url='/login/')
  def changePassword(request):
    if request.method == "POST":
      passwordForm = PasswordChangeForm(data=request.POST, user=request.user)
      if passwordForm.is_valid():
        passwordForm.save()
        update_session_auth_hash(request, passwordForm.user)
        messages.success(request, "Password was changed successfully.", extra_tags="alert-success")
        return redirect(reverse('profile'))
      else:
        messages.error(request, "Couldn't change the password. Please, try again.", extra_tags="alert-danger")
        return redirect(reverse('profile'))
    else:
      raise PermissionDenied

  @staticmethod
  def logout(request):
    logout_auth(request)
    return redirect(reverse('home'))

  @staticmethod
  def signup(request):
    if request.method == "POST":
      form = forms.SignUp(request.POST)
      if form.is_valid():
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        form.save()
        user = authenticate(username=username, password=password)
        if user is not None:
          login_auth(request, user)
          return redirect(reverse('profile'))
    else:
      form = forms.SignUp()
    if request.GET.get('modal') == '1':
      base = 'modalForm.html'
    else:
      base = 'form.html'
    
    return render(request, "SingUp.html", {'form': form, 'base':base})

  @login_required(login_url='/login/')
  def addWalletAddress(request):
    message = "Raffle Confirm Wallet %s" %str(datetime.datetime.now())
    if request.GET.get('modal') == '1':
      base = 'modalForm.html'
    else:
      base = 'form.html'

    if request.method == "POST":
      form = forms.AddWalletAddress(request.POST, instance=request.user)
      try:
        is_valid = form.is_valid()
      except Exception as e:
        print(e)
        is_valid = False

      if is_valid:
        form.save() 
        messages.success(request, "Address registered sucessfully.", extra_tags="alert-success")
        return redirect(reverse('profile'))
      else:
        return render(request, "addWalletAddress.html", {'form': form, 'base': base})
    else:
      request.user.message = message
      request.user.save()
      form = forms.AddWalletAddress(
            initial={'final_message':message,
                     'user_pk':request.user.pk,
                     'signature':'',
                     'wallet_address':'',
                     'public_key':'', }
          )
    
    return render(request, "addWalletAddress.html", {'form': form, 'base': base})

  @staticmethod
  @login_required(login_url='/login/')
  def profile(request):
    return render(request, "profile.html")

  @staticmethod
  def notifications(request):
    if request.user.is_anonymous:
      return JsonResponse({})      
    if request.method == "GET":
      notifications = [] 
      for tx in request.user.transactions.filter(notified=False):
        notifications.append({
            'message': "You have purchased %d %s."%(
                tx.boughtTicket, 
                "ticket" if tx.boughtTicket == 1 else "tickets" 
              )
          })
        tx.notified = True
        tx.save()

      return JsonResponse({'notifications': notifications})
    else:
      raise PermissionDenied  


  @staticmethod
  def getUsers(request):
      id_users = request.GET.get('id_users')
      options = '<option value="11" selected="selected">---------</option>'
      if id_users:
          users = models.User.objects.filter(username__contains=id_users)   
      for user in users:
          options += '<option value="%s">%s</option>' % (
              user.pk,
              user.username
          )
      response = {}
      response['signers'] = options
      return JsonResponse(response)
