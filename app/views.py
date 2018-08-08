
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
from app.models import call
# Create your views here.


def index(request):
  raffles = models.Raffle.objects.all()
  return render(request, "index.xhtml", {"raffles":raffles})

class User:
  def login(request):
    if request.method == "POST":
      form = forms.Login(request.POST)
      if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
          login_auth(request, user)
          return redirect(request.GET.get('next',reverse('index')))
        else:
          messages.error(request, "Bad email or password.")
          
    else:
      form = forms.Login()
    
    return render(request, "form.html", {'form': form})    

  def logout(request):
    logout_auth(request)
    return redirect(reverse('index'))

  def signup(request):
    if request.method == "POST":
      form = forms.SignUp(request.POST)
      if form.is_valid():
        print(form.cleaned_data)
        form.save()
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=email, password=password)
        if user is not None:
          login_auth(request, user)
          return redirect(reverse('index'))
    else:
      form = forms.SignUp()
    
    return render(request, "form.html", {'form': form})

  @login_required(login_url='/login/')
  def addWalletAddress(request):
    message = "Raffle Confirm Wallet %s" %str(datetime.datetime.now())
    if request.method == "POST":
      form = forms.AddWalletAddress(request.POST, instance=request.user)
      if form.is_valid():
        address = form.cleaned_data['wallet_address']
        signature = form.cleaned_data['signature']
        final_message = form.cleaned_data['final_message']
        if request.user.message == final_message:
          if call(["verifymessage", address, signature, final_message]):
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

  def profile(request):
    return render(request, "profile.html")    
    

class Raffle:
  def details(request, id):
    try:
      raffle = models.Raffle.objects.get(id=id)
    except:
      raffle = None
    try:
      count = int(call(["getblockcount"]))
      address = call(["getnewaddress"])
      blockHash = call(['getblockhash', str(count)])
      blockTime = call(['getblock', blockHash])['time']

    except Exception as e:
      raise PermissionDenied
    raffle.getWinner()
    prize = call(['getaddressbalance', json.dumps({'addresses':[raffle.addressPrize]})])['balance']/100000000 #<- satoshis
    if not prize:
      prize = 0

    date = datetime.datetime.fromtimestamp(blockTime + (raffle.blockHeight-count) * (2.6*60))
    return render(request, "raffle.html", {"raffle":raffle, 'date':date, 'prize': prize})

  @login_required(login_url='/login/')
  def createRaffle(request):
    if request.method == "POST":
      form = forms.Raffle(request.POST)
      if form.is_valid():
        raffle = form.save()
        raffle.owner = request.user
        if not raffle.isMultisig:
          raffle.addressPrize = call(['getnewaddress']).replace('\n','')
        raffle.save()
        return redirect(raffle)
      else:
        try:
          count = int(call(["getblockcount"]))
          address = call(["getnewaddress"])
          blockHash = call(['getblockhash', str(count)])
          blockTime = call(['getblock', blockHash])['time']
      
        except Exception as e:
          print(e)
          raise PermissionDenied
    else:        
      try:
        count = int(call(["getblockcount"]))
        address = call(["getnewaddress"])
        blockHash = call(['getblockhash', str(count)])
        blockTime = call(['getblock', blockHash])['time']
      
      except Exception as e:
        print(e)
        raise PermissionDenied
      form = forms.Raffle(initial={'blockHeight':count, 'address':address})

    return render(request, "createRaffle.html", {'form': form, 'blockTime': blockTime, 'count': count})

  def buyTicket(request, id):
    # if request.user.wallet_address is None:
    #    messages.error(request, "Before buying a ticket, you've to add a wallet addres in your profile." )
    #    return redirect(reverse("profile"))
    try:
      raffle = models.Raffle.objects.get(id=id)
    except:
      raffle = None
    if raffle:
      if request.user:
        addressGenerated = models.AddressGenerated.objects.filter(user=request.user, raffle=raffle)
        if addressGenerated.exists():
          address = addressGenerated[0].address
        else:
          address = call(["getnewaddress"]).replace("\n", "")
          addressGenerated = models.AddressGenerated(user=request.user, raffle=raffle, address=address)
          addressGenerated.save()
      else:
        try:
          anonUser = User.objects.get(email="anonymous@admin.com")
        except Exception as e:
          print(e)
          print("Anonymous user doesn't exists.")
          raise PermissionDenied
        address = call(["getnewaddress"]).replace("\n", "")
        addressGenerated = models.AddressGenerated(user=anonUser, raffle=raffle, address=address)
        addressGenerated.save()
      
    else:
      messages.error(request, "raffle not found.")
    return render(request, "buyTicket.html", {
        'address': address,
        'raffle': raffle
      })
  
  @login_required(login_url='/login/')
  def addPrivkey(request, id):
    try:
      raffle = models.Raffle.objects.get(id=id)
    except:
      raise PermissionDenied

    if not (raffle.finished and request.user in raffle.signers.all()):
      raise PermissionDenied
    msg = ""
    if request.method == "POST":
      form = forms.AddPrivkey(request.POST)
      if form.is_valid():
        msg = raffle.addPrivKey(form.cleaned_data['privkey'])
        raffle.save()
    else:
      form = forms.AddPrivkey()

    return render(request, "form.html", {'form': form, "msg":msg}) 












