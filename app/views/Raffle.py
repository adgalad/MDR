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
from app.views.views import handler400, handler403, handler404
from app.dash import Dash

class Raffle:
  @staticmethod
  def active(request):
    count = Dash.getblockcount()
    activeRaffles = models.Raffle.objects.filter(is_active=True).order_by('-created_at')
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
  @login_required(login_url='/login/')
  def myRaffles(request):
    count = Dash.getblockcount()
    user = request.user
    activeRaffles = user.ownsRaffles.all().order_by('-created_at')
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
      return handler403(request)
    if not raffle.is_active:
      return redirect(reverse('payRaffle', kwargs={'id':id}))
    return render(request, "raffle.html", {"raffle":raffle})

  @staticmethod
  def moreDetails(request, id):
    try:
      raffle = models.Raffle.objects.get(id=id)
    except:
      return handler403(request)
      
    if not raffle.is_active:
      return redirect(reverse('payRaffle', kwargs={'id':id}))
    return render(request, "raffleDetails.html", {"raffle":raffle})

  @staticmethod
  @login_required(login_url='/login/')
  def finished(request,id):
    try:
      raffle = models.Raffle.objects.get(pk=id)
    except Exception as e:
      return handler403(request)

    if raffle.owner != request.user and not request.user.is_superuser:
      return handler403(request)
      
    if not raffle.finished:
      return handler403(request)
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
          address = Dash.getnewaddress()
          pubkey = Dash.validateaddress(address)['pubkey']
          if request.user.wallet_address:
            raffle = models.Raffle.objects.create(
                        name=form.cleaned_data['name'],
                        thumbnail_url=form.cleaned_data['thumbnail_url'],
                        type=raffleType,
                        description=form.cleaned_data['description'],
                        summary=form.cleaned_data['summary'],
                        ticketPrice=models.rafflePrice[raffleType],
                        drawDate=timezone.now() + datetime.timedelta(days=models.raffleDuration[raffleType]),
                        owner = request.user,
                        addressProject=request.user.wallet_address,
                        MSpubkey1=request.user.public_key,
                        # MSpubkey2=form.cleaned_data['signers'].wallet_address,
                        MSpubkey2=pubkey,
                        MSaddress=address
                      )
            
            # raffle.signers.add(form.cleaned_data['signers'])
            raffle.createMultisigAddress()
            raffle.save()
            return redirect(raffle)
          else:
            messages.error(request, "Couldn't create multisig address.")

        except Exception as e:
          print(e)
          print("No entiendo")
          return handler403(request)
    else:
      form = forms.Raffle()

    return render(request, "createRaffle.html", {'form': form,})

  @staticmethod
  @login_required(login_url='/login/')
  def edit(request, id):
    try:
      raffle = models.Raffle.objects.get(pk=id)
    except:
      return handler403(request)

    if raffle.owner != request.user:
      return handler403(request)

    if request.method == "POST":
      form = forms.EditRaffle(request.POST, instance=raffle)
      if form.is_valid():
        form.save()
        return redirect(reverse('raffleDetails', kwargs={'id':id}))
      return render(request, "editRaffle.html", {'form':form})
    else:
      form = forms.EditRaffle(instance=raffle)
      return render(request, "editRaffle.html", {'form':form})

  @staticmethod
  @login_required(login_url='/login/')
  def pay(request, id):
    try:
      raffle = models.Raffle.objects.get(pk=id)
    except:
      return handler403(request)

    if raffle.owner != request.user and not request.user.is_superuser:
      return handler403(request)
    if request.GET.get('modal') == '1':
      base = 'modalForm.html'
    else:
      base = 'form.html'

    return render(request, "payRaffle.html", {"raffle":raffle, "base":base})

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
        return handler403(request)
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
  
  # @staticmethod
  # @login_required(login_url='/login/')
  # def addPrivkey(request, id):
  #   try:
  #     raffle = models.Raffle.objects.get(id=id)
  #   except:
  #     return handler403(request)

  #   # if not (raffle.finished and request.user in raffle.signers.all()):
  #   if True:
  #     return handler403(request)
  #   msg = ""
  #   if request.method == "POST":
  #     form = forms.AddPrivkey(request.POST)
  #     if form.is_valid():
  #       msg = raffle.addPrivKey(form.cleaned_data['privkey'])
  #       raffle.save()
  #   else:
  #     form = forms.AddPrivkey()

  #   return render(request, "form.html", {'form': form, "msg":msg}) 
