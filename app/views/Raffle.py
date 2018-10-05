import json
import datetime

from django.http import HttpResponseServerError
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
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
      raise PermissionDenied

    # try:
    #   count = Dash.getblockcount()
    #   address = Dash.getnewaddress()
    #   blockHash = Dash.getblockhash(count)
    #   blockTime = Dash.getblock(blockHash)['time']

    # except Exception as e:
    #   raise PermissionDenied
    balance = 1000#Dash.getaddressbalance([raffle.addressPrize])['received']
    prize = balance/100000000 #<- satoshis
    #print(">>", balance, prize)
    if not prize or prize < 0:
      prize = 0
    # if raffle.winnerAddress:
    #   date = datetime.datetime.fromtimestamp(blockTime)
    # else:
    #   date = datetime.datetime.fromtimestamp(blockTime + (raffle.blockHeight-count) * (2.6*60))
    return render(request, "raffle.html", {"raffle":raffle, 'date':raffle.getDate, 'prize': prize})

  def moreDetails(request, id):
    try:
      raffle = models.Raffle.objects.get(id=id)
    except:
      raise PermissionDenied

    # try:
    #   count = Dash.getblockcount()
    #   address = Dash.getnewaddress()
    #   blockHash = Dash.getblockhash(count)
    #   blockTime = Dash.getblock(blockHash)['time']

    # except Exception as e:
    #   raise PermissionDenied
    balance = 1000#Dash.getaddressbalance([raffle.addressPrize])['received']
    prize = balance/100000000 #<- satoshis
    #print(">>", balance, prize)
    if not prize or prize < 0:
      prize = 0
    
    return render(request, "raffleDetails.html", {"raffle":raffle, 'prize': prize})

  @staticmethod
  @login_required(login_url='/login/')
  def createRaffle(request):
    if request.method == "POST":
      form = forms.Raffle(request.POST)
      print(request.POST)
      if form.is_valid():
        try:
          rtype = form.cleaned_data['type']
          address = Dash.getnewaddress()
          raffle = models.Raffle.objects.create(
                      name=form.cleaned_data['name'],
                      thumbnail_url=form.cleaned_data['thumbnail_url'],
                      type=rtype,
                      description=form.cleaned_data['description'],
                      ticketPrice=models.rafflePrice[rtype],
                      drawDate=timezone.now() + datetime.timedelta(days=models.raffleDuration[rtype]),
                      MSpubkey1 = address,
                      owner = request.user,
                      addressProject=request.user.wallet_address
                    )
          
          
          # raffle.signers.add(form.cleaned_data['signers'])
          # # if not raffle.isMultisig:
          

          # raffle.createMultisigAddress()
          # raffle.save()
          return redirect(raffle)
      # else:
      #   try:
      #     count = Dash.getblockcount()
      #     address = Dash.getnewaddress()
      #     blockHash = Dash.getblockhash(count)
      #     blockTime = Dash.getblock(blockHash)['time']
      
        except Exception as e:
          print(e)
          raise PermissionDenied
    else:
      form = forms.Raffle()

    return render(request, "createRaffle.html", {'form': form,})

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
        address = addressGenerated[0].address.replace("\n", "")
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