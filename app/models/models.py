import json
import random
import datetime

from django.db import models

from app.dash import Dash
from app.models.User import User

class Transaction(models.Model):
  address = models.CharField(max_length=100, primary_key=True)
  user   = models.ForeignKey(User, related_name="transactions")
  amount = models.DecimalField(max_digits=20, decimal_places=6)
  raffle = models.ForeignKey("Raffle", related_name="transactions")
  blockHeight = models.IntegerField(verbose_name="Block Height")
  boughtTicket = models.IntegerField(verbose_name="Bought Tickets")
  
  def __str__(self):
    return str((self.user, self.address))

  @property
  def getDate(self):

    rawTransaction = Dash.getrawtransaction(self.address)
    timestamp = rawTransaction['time']
    return datetime.datetime.fromtimestamp(timestamp)


class AddressGenerated(models.Model):
  user    = models.ForeignKey(User)
  raffle  = models.ForeignKey("Raffle", related_name="addresses")
  address = models.CharField(unique=True, max_length=64, verbose_name='Address')


  def __str__(self):
    return str((self.user, self.address))
