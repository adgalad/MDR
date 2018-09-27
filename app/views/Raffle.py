import json
import datetime

from django.http import HttpResponseServerError
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from app import models, forms
from app.dash import Dash

class Raffle:
  @staticmethod
  def active(request):
    count = Dash.getblockcount()
    activeRaffles = models.Raffle.objects.all()
    return render(request, "raffles.html", {'activeRaffles': activeRaffles})    

  @staticmethod
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
  @staticmethod
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
          count = Dash.getblockcount()
          address = Dash.getnewaddress()
          blockHash = Dash.getblockhash(count)
          blockTime = Dash.getblock(blockHash)['time']
      
        except Exception as e:
          #print(e)
          raise PermissionDenied
    else:        
      try:
        count = Dash.getblockcount()
        address = Dash.getnewaddress()
        blockHash = Dash.getblockhash(count)
        blockTime = Dash.getblock(blockHash)['time']
      
      except Exception as e:
        #print(e)
        raise PermissionDenied
    form = forms.Raffle(initial={'blockHeight':count, 'address':address})

    return render(request, "createRaffle.html", {'form': form, 'blockTime': blockTime, 'count': count})

  @staticmethod
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
  @staticmethod
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