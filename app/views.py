
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
from app.models import Dash
# Create your views here.

from raffle.settings import DASH_CLI, RPC_SERVER, RPC_PORT, RPC_USER, RPC_PASSWORD, DEFAULT_FROM_EMAIL


def index(request):
  #print(DASH_CLI, RPC_SERVER, RPC_PORT, RPC_USER, RPC_PASSWORD, DEFAULT_FROM_EMAIL)
  raffles = models.Raffle.objects.all()
  return render(request, "index.xhtml", {"raffles":raffles})

def help(request):
    return render(request, "help.html")  


class User:
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
    
    return render(request, "form.html", {'form': form})    

  def logout(request):
    logout_auth(request)
    return redirect(reverse('index'))

  def signup(request):
    if request.method == "POST":
      form = forms.SignUp(request.POST)
      if form.is_valid():
        #print(form.cleaned_data)
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
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

  def profile(request):
    return render(request, "profile.html")  
    
class Raffle:
  def details(request, id):
    try:
      raffle = models.Raffle.objects.get(id=id)
    except:
      raffle = None
    # try:
    #   count = Dash.getblockcount()
    #   address = Dash.getnewaddress()
    #   blockHash = Dash.getblockhash(count)
    #   blockTime = Dash.getblock(blockHash)['time']

    # except Exception as e:
    #   raise PermissionDenied
    balance = Dash.getaddressbalance([raffle.addressPrize])['received']
    prize = balance/100000000 #<- satoshis
    #print(">>", balance, prize)
    if not prize or prize < 0:
      prize = 0
    # if raffle.winnerAddress:
    #   date = datetime.datetime.fromtimestamp(blockTime)
    # else:
    #   date = datetime.datetime.fromtimestamp(blockTime + (raffle.blockHeight-count) * (2.6*60))
    return render(request, "raffle.html", {"raffle":raffle, 'date':raffle.getDate, 'prize': prize})

  @login_required(login_url='/login/')
  def createRaffle(request):
    if request.method == "POST":
      form = forms.Raffle(request.POST)
      if form.is_valid():
        raffle = form.save()
        raffle.owner = request.user
        if not raffle.isMultisig:
          address = Dash.getnewaddress()
          raffle.MSpubkey1 = address
          raffle.signsRequired = 1
          raffle.privkey1 = Dash.dumpprivkey(address)
          raffle.save()
          raffle.createMultisigAddress()
        raffle.save()
        return redirect(raffle)
      else:
        try:
          # count = Dash.getblockcount()
          # address = Dash.getnewaddress()
          # blockHash = Dash.getblockhash(count)
          # blockTime = Dash.getblock(blockHash)['time']
          count = 112#Dash.getblockcount()
          address = 'xasdasdax3'#Dash.getnewaddress()
          # blockHash = Dash.getblockhash(count)
          blockTime = 123#Dash.getblock(blockHash)['time']
      
        except Exception as e:
          #print(e)
          raise PermissionDenied
    else:        
      try:
        count = 112#Dash.getblockcount()
        address = 'xasdasdax3'#Dash.getnewaddress()
        # blockHash = Dash.getblockhash(count)
        blockTime = 123#Dash.getblock(blockHash)['time']
      
      except Exception as e:
        #print(e)
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
      try:
        user = request.user if not request.user.is_anonymous else models.User.objects.get(username="Anonymous")
      except Exception as e:
        #print("Missing Anonymous user")
        raise PermissionDenied
      addressGenerated = models.AddressGenerated.objects.filter(user=user, raffle=raffle)
      if addressGenerated.exists():
        address = addressGenerated[0].address
      else:
        address = Dash.getnewaddress().replace("\n", "")
        addressGenerated = models.AddressGenerated(user=user, raffle=raffle, address=address)
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