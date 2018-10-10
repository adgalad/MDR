import json
import datetime

from django.contrib import messages
from django.http import HttpResponseServerError
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
    activeRaffles = models.Raffle.objects.filter(drawDate__gt=timezone.now()).order_by('drawDate')
    page = request.GET.get('page', 1)
    paginator = Paginator(activeRaffles, 10)
    try:
        numbers = paginator.page(page)
    except PageNotAnInteger:
        numbers = paginator.page(1)
    except EmptyPage:
        numbers = paginator.page(paginator.num_pages)
    return render(request, "raffles.html", {'numbers': numbers})

  @staticmethod
  def myRaffles(request):
    count = Dash.getblockcount()
    user = request.user
    activeRaffles = models.Raffle.objects.filter(owner=user).order_by('-drawDate')
    page = request.GET.get('page', 1)
    paginator = Paginator(activeRaffles, 10)
    try:
        numbers = paginator.page(page)
    except PageNotAnInteger:
        numbers = paginator.page(1)
    except EmptyPage:
        numbers = paginator.page(paginator.num_pages)
    return render(request, "rafflesUser.html", {'numbers': numbers})    


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
    return render(request, "raffle.html", {"raffle":raffle, 'prize': prize})

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
  def finished(request,id):
    raffle = models.Raffle.objects.get(pk=id)
    if raffle.owner != request.user and not request.user.is_superuser:
      raise PermissionDenied
    return render(request, "finishedRaffle.html", {"raffle":raffle})

  @staticmethod
  @login_required(login_url='/login/')
  def createRaffle(request):
    if not request.user.wallet_address:
      return redirect(reverse('addWalletAddress'))
    if request.method == "POST":
      form = forms.Raffle(request.POST)
      if form.is_valid():
        try:
          raffleType = form.cleaned_data['type']
          admin = models.User.objects.get(email='admin@admin.com')
          address = Dash.getnewaddress()
          pubkey = Dash.validateaddress(address)['pubkey']
          if request.user.wallet_address and form.cleaned_data['signers'].wallet_address and admin[0].wallet_address:
            raffle = models.Raffle.objects.create(
                        name=form.cleaned_data['name'],
                        thumbnail_url=form.cleaned_data['thumbnail_url'],
                        type=raffleType,
                        description=form.cleaned_data['description'],
                        ticketPrice=models.rafflePrice[raffleType],
                        drawDate=timezone.now() + datetime.timedelta(days=models.raffleDuration[raffleType]),
                        owner = request.user,
                        addressProject=request.user.wallet_address,
                        MSpubkey1=request.user.public_key,
                        # MSpubkey2=form.cleaned_data['signers'].wallet_address,
                        MSpubkey2=pubkey
                      )
            
            # raffle.signers.add(form.cleaned_data['signers'])
            raffle.createMultisigAddress()
            raffle.save()
            return redirect(raffle)
          else:
            messages.error(request, "Couldn't create multisig address.")
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
